from flask import Flask, render_template, request
from flask_socketio import SocketIO
from sqlalchemy import create_engine, text
import pandas as pd
import plotly.express as px
from pipeline import executar_pipeline_completo 

# --- Configurações ---
db_config = { 'user': 'root', 'password': 'senac', 'host': 'localhost', 'port': 3306, 'database': 'mineracao_db' }
engine = create_engine(f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

app = Flask(__name__)
socketio = SocketIO(app) 

# --- ROTA 1: Página Principal (Home) ---
@app.route("/")
def home():
    return render_template("home.html")

# --- ROTA 2: Página de Resultados  ---
@app.route("/resultados")
def resultados():
    
    termo = request.args.get('termo', '')
    preco_min = request.args.get('preco_min', '')
    preco_max = request.args.get('preco_max', '')
    avaliacao = request.args.get('avaliacao', '')
    
    base_query = "SELECT * FROM jogos WHERE 1=1"
    params = {}

    if termo:
        base_query += " AND titulo LIKE :termo"
        params['termo'] = f"%{termo}%"
    if preco_min:
        base_query += " AND preco_numerico >= :preco_min"
        params['preco_min'] = float(preco_min)
    if preco_max:
        base_query += " AND preco_numerico <= :preco_max"
        params['preco_max'] = float(preco_max)
    if avaliacao:
        base_query += " AND avaliacao_texto = :avaliacao"
        params['avaliacao'] = avaliacao

    df_resultados = pd.read_sql(text(base_query), engine, params=params)
    total_jogos = len(df_resultados)
    
    resultados_html = None
    grafico_preco_html = ""
    grafico_avaliacao_html = ""
    grafico_boxplot_html = ""
    grafico_scatter_html = ""

    if not df_resultados.empty:
        
        df_para_exibicao = df_resultados[['titulo', 'preco_numerico', 'avaliacao_texto', 'total_avaliacoes']].head(20).copy()
        df_para_exibicao.rename(columns={ 'titulo': 'Título', 'preco_numerico': 'Preço (R$)', 'avaliacao_texto': 'Avaliação', 'total_avaliacoes': 'Nº de Avaliações' }, inplace=True)
        resultados_html = df_para_exibicao.to_html(classes='table', index=False, justify='left')
        
        
        fig_preco = px.histogram(df_resultados, x="preco_numerico", nbins=20, title="Distribuição de Preços nos Resultados", labels={'preco_numerico': 'Faixa de Preço (R$)', 'count': 'Quantidade de Jogos'})
        fig_preco.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c7d5e0', bargap=0.2)
        fig_preco.update_yaxes(title_text='Quantidade de Jogos')
        fig_preco.update_traces(marker_line_color='#66c0f4', marker_line_width=1.5)
        grafico_preco_html = fig_preco.to_html(full_html=False)

        df_counts = df_resultados['avaliacao_texto'].value_counts().reset_index()
        df_counts.columns = ['avaliacao_texto', 'count']
        fig_avaliacao = px.bar(df_counts, x='avaliacao_texto', y='count', title="Contagem de Avaliações nos Resultados", labels={'avaliacao_texto': 'Tipo de Avaliação', 'count': 'Quantidade de Jogos'})
        fig_avaliacao.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c7d5e0', bargap=0.2)
        fig_avaliacao.update_xaxes(categoryorder='total descending', title_text='Tipo de Avaliação') 
        fig_avaliacao.update_yaxes(title_text='Quantidade de Jogos') 
        fig_avaliacao.update_traces(marker_line_color='#66c0f4', marker_line_width=1.5)
        grafico_avaliacao_html = fig_avaliacao.to_html(full_html=False)

        # 'df_resultados' é o DataFrame com os dados filtrados
        fig_boxplot = px.box(
        df_resultados, 
        x='avaliacao_texto', 
        y='preco_numerico', 
        title='Distribuição de Preço por Tipo de Avaliação',
        labels={'avaliacao_texto': 'Tipo de Avaliação', 'preco_numerico': 'Preço (R$)'},
        hover_name='titulo') 
        fig_boxplot.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c7d5e0')
        fig_boxplot.update_xaxes(categoryorder='total descending')
        grafico_boxplot_html = fig_boxplot.to_html(full_html=False)

        # Filtra dados para o scatter plot para evitar erros com log(0)
        df_scatter_data = df_resultados[df_resultados['total_avaliacoes'] > 0].copy()
        fig_scatter = px.scatter(
        df_scatter_data,
        x='total_avaliacoes',
        y='preco_numerico',
        title='Popularidade (Nº de Reviews) vs. Preço',
        labels={'total_avaliacoes': 'Total de Avaliações (Escala Log)', 'preco_numerico': 'Preço (R$)', 'porcentagem_aval': '% Positivas'},
        log_x=True,  
        color='porcentagem_aval', 
        size='porcentagem_aval', 
        hover_name='titulo') 
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c7d5e0')
        grafico_scatter_html = fig_scatter.to_html(full_html=False)

    return render_template(
        "resultados.html",
        resultados_html=resultados_html,
        total_jogos=total_jogos,
        grafico_preco=grafico_preco_html, 
        grafico_avaliacao=grafico_avaliacao_html, 
        grafico_boxplot=grafico_boxplot_html,
        grafico_scatter=grafico_scatter_html
    )

# --- LÓGICA DO SOCKET.IO PARA MINERAÇÃO ---
@socketio.on('iniciar_mineracao')
def handle_mining_event():
    print("Evento 'iniciar_mineracao' recebido. Iniciando a tarefa em segundo plano.")
    socketio.start_background_task(executar_pipeline_completo, engine, socketio)

# --- Execução da Aplicação ---
if __name__ == "__main__":
    # Usa socketio.run() em vez de app.run()
    socketio.run(app, debug=True)