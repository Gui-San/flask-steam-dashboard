# --- Importações Essenciais ---
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
from sqlalchemy import create_engine, text

# --- Configurações do Banco de Dados ---
db_config = { 'user': 'root', 'password': 'senac', 'host': 'localhost', 'port': 3306, 'database': 'mineracao_db' }

# --- FUNÇÃO 1: Preparar o Banco de Dados ---
def setup_database(engine):
    """Garante que a tabela 'jogos' exista no banco de dados."""
    try:
        with engine.connect() as connection:
            sql_create_table = text("""
            CREATE TABLE IF NOT EXISTS jogos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL UNIQUE,
                preco_numerico DECIMAL(10, 2),
                avaliacao_texto VARCHAR(50),
                score_avaliacao INT,
                porcentagem_aval INT,
                total_avaliacoes INT,
                data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """)
            connection.execute(sql_create_table)
            connection.commit()
    except Exception as e:
        print(f"Erro ao configurar o banco de dados: {e}")
        raise

# --- FUNÇÃO 2: Coletar Dados (Para emitir status) ---
def coletar_dados_steam(socketio=None):
    def emit_status(msg):
        if socketio:
            socketio.emit('update_status', {'msg': msg, 'type': 'info'})
            socketio.sleep(0.1)

    URL = "https://store.steampowered.com/search/?filter=topsellers&ignore_preferences=1"
    emit_status(f"Iniciando coleta de '{URL}'...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    
    driver = webdriver.Chrome(options=options)
    emit_status("Navegador iniciado. Acessando a página...")
    driver.get(URL)
    emit_status("Iniciando scroll para carregar todos os jogos...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
    emit_status("Scroll completo. Extraindo dados da página...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    lista_jogos = soup.find_all('a', class_='search_result_row')
    dados_coletados = []
    
    for jogo in lista_jogos:
        titulo = jogo.find('span', class_='title').text
        preco_tag = jogo.find('div', class_='discount_final_price')
        if not preco_tag:
            preco_tag = jogo.find('div', class_='search_price')
        preco_bruto = preco_tag.text.strip().split('R$')[-1].strip() if preco_tag else "0"
        
        avaliacao_texto = "Sem avaliação"
        porcentagem_aval = 0
        total_avaliacoes = 0
        avaliacao_tag = jogo.find('span', class_='search_review_summary')
        
        if avaliacao_tag and avaliacao_tag.has_attr('data-tooltip-html'):
            tooltip_text = avaliacao_tag['data-tooltip-html']
            avaliacao_texto = tooltip_text.split('<br>')[0].strip()
            match_percent = re.search(r'(\d+)%', tooltip_text)
            match_total = re.search(r'([\d,]+) análises', tooltip_text)
            if match_percent:
                porcentagem_aval = int(match_percent.group(1))
            if match_total:
                total_avaliacoes = int(match_total.group(1).replace(',', ''))
                
        dados_coletados.append({
            'titulo': titulo, 'preco_bruto': preco_bruto, 'avaliacao_texto': avaliacao_texto,
            'porcentagem_aval': porcentagem_aval, 'total_avaliacoes': total_avaliacoes
        })
        
    emit_status(f"Coleta finalizada. {len(dados_coletados)} registros encontrados.")
    return pd.DataFrame(dados_coletados)

# --- FUNÇÃO 3: Tratar e Limpar os Dados ---
def tratar_dados(df_bruto):
    df = df_bruto.copy()
    
    df['preco_numerico'] = df['preco_bruto'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['preco_numerico'] = pd.to_numeric(df['preco_numerico'], errors='coerce').fillna(0)
    
    df['avaliacao_texto'] = df['avaliacao_texto'].str.strip()
    mapa_avaliacao = {
        "Extremamente positivas": 10, "Muito positivas": 9, "Positivas": 8, "Ligeiramente positivas": 7,
        "Análises Variadas": 6, "Ligeiramente negativas": 5, "Negativas": 4, "Muito negativas": 3,
        "Extremamente negativas": 2, "Sem avaliação": 0
    }
    df['score_avaliacao'] = df['avaliacao_texto'].map(mapa_avaliacao).fillna(0).astype(int)
    
    df['porcentagem_aval'] = df['porcentagem_aval'].astype(int)
    df['total_avaliacoes'] = df['total_avaliacoes'].astype(int)
    
    df_limpo = df[['titulo', 'preco_numerico', 'avaliacao_texto', 'score_avaliacao', 'porcentagem_aval', 'total_avaliacoes']]
    df_limpo.dropna(subset=['titulo'], inplace=True)
    
    return df_limpo

# --- FUNÇÃO 4: Inserir ou Atualizar Dados no Banco ---
def inserir_ou_atualizar_dados(df, engine):
    update_query = text("""
        UPDATE jogos SET preco_numerico = :preco_numerico, avaliacao_texto = :avaliacao_texto, 
        score_avaliacao = :score_avaliacao, porcentagem_aval = :porcentagem_aval, 
        total_avaliacoes = :total_avaliacoes WHERE titulo = :titulo
    """)
    insert_query = text("""
        INSERT INTO jogos (titulo, preco_numerico, avaliacao_texto, score_avaliacao, porcentagem_aval, total_avaliacoes) 
        VALUES (:titulo, :preco_numerico, :avaliacao_texto, :score_avaliacao, :porcentagem_aval, :total_avaliacoes)
    """)
    
    jogos_novos = 0
    jogos_atualizados = 0
    
    with engine.connect() as connection:
        for index, row in df.iterrows():
            result = connection.execute(update_query, parameters=row.to_dict())
            if result.rowcount == 0:
                connection.execute(insert_query, parameters=row.to_dict())
                jogos_novos += 1
            else:
                jogos_atualizados += 1
        connection.commit()
    return (jogos_novos, jogos_atualizados)

# --- FUNÇÃO PRINCIPAL PARA O PIPELINE ---
def executar_pipeline_completo(engine, socketio=None):
    def emit_status(msg, type='info'):
        if socketio:
            socketio.emit('update_status', {'msg': msg, 'type': type})
            socketio.sleep(0.1)
    try:
        emit_status(">>> INICIANDO PIPELINE COMPLETO <<<")
        setup_database(engine)
        emit_status("Banco de dados verificado.")
        
        dados_brutos = coletar_dados_steam(socketio)
        if not dados_brutos.empty:
            dados_limpos = tratar_dados(dados_brutos)
            emit_status("Dados tratados e limpos.")
            
            novos, atualizados = inserir_ou_atualizar_dados(dados_limpos, engine)
            emit_status(f"Dados salvos: {novos} novos, {atualizados} atualizados.")
        else:
            emit_status("Nenhum dado foi coletado da Steam.")
        
        if socketio:
            socketio.emit('mineracao_concluida', {'msg': '>>> PROCESSO FINALIZADO COM SUCESSO! <<<'})
    except Exception as e:
        error_msg = f"ERRO NO PIPELINE: {e}"
        print(error_msg)
        if socketio:
            socketio.emit('update_status', {'msg': error_msg, 'type': 'error'})
            socketio.emit('mineracao_concluida', {'msg': '>>> PROCESSO FINALIZADO COM ERRO! <<<'})

# Bloco para execução manual 
if __name__ == "__main__":
    print("Executando o pipeline manualmente...")
    db_engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    executar_pipeline_completo(db_engine)