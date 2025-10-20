# 🚀 Aplicação Web de Busca e Mineração da Steam (Flask)

Este projeto é uma aplicação web full-stack desenvolvida com Flask que permite aos usuários:
1.  **Executar** um pipeline de web scraping (mineração de dados) da Steam com um único clique.
2.  **Acompanhar** o progresso da coleta em tempo real via SocketIO.
3.  **Consultar** o banco de dados de jogos com filtros de nome, preço e avaliação.
4.  **Visualizar** dashboards interativos (Plotly) gerados a partir dos dados filtrados.

Este projeto é a evolução de um script de pipeline anterior (`mineracao-steam-mysql`), transformando-o em uma ferramenta de UI/UX amigável para usuários não-técnicos.

## 📸 Screenshots

<img width="1366" height="768" alt="Inicio mineracao" src="https://github.com/user-attachments/assets/c8fe57ee-fbff-4f13-bfed-b9e8c7f3ad53" />

<img width="1366" height="768" alt="descricao no scatter" src="https://github.com/user-attachments/assets/6845b028-3bb0-4c76-a95e-3b719ee993f3" />


---

## 🛠️ Pilha de Tecnologias

* **Backend:** Flask, Flask-SocketIO
* **Coleta de Dados:** Selenium, BeautifulSoup4
* **Banco de Dados:** MySQL (comunicação via SQLAlchemy, PyMySQL)
* **Frontend/Visualização:** HTML, CSS, JavaScript (Socket.IO client), Plotly
* **Manipulação de Dados:** Pandas

---

## 🌟 Principais Funcionalidades

* **Mineração com Um Clique:** O usuário pode iniciar o pipeline completo de coleta e armazenamento através de um botão na interface.
* **Log em Tempo Real:** A interface exibe o status do processo de mineração em tempo real, informando o usuário sobre cada etapa (iniciando o navegador, scroll, coleta, salvamento no BD).
* **Filtragem Dinâmica:** A página de resultados permite consultas complexas ao banco de dados, filtrando por nome, faixa de preço e tipo de avaliação.
* **Dashboards Interativos:** Os gráficos de Plotly na página de resultados são interativos, permitindo zoom e exibindo informações detalhadas ao passar o mouse.

---

## 🚀 Como Executar Localmente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Gui-San/flask-steam-dashboard.git](https://github.com/Gui-San/flask-steam-dashboard.git)
    cd flask-steam-dashboard
    ```
2.  **(Recomendado) Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure o Banco de Dados:**
    * Certifique-se de ter um servidor MySQL rodando.
    * Crie um banco de dados (ex: `mineracao_db`).
    * Ajuste as credenciais (`user`, `password`, `host`) no dicionário `db_config` dentro de `app.py` e `pipeline.py`.
5.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
6.  Abra seu navegador e acesse: `http://127.0.0.1:5000`

---
<br>



# 🚀 Steam Search & Mining Web App (Flask)

This is a full-stack web application built with Flask that allows users to:
1.  **Run** a Steam web scraping pipeline with a single click.
2.  **Monitor** the collection progress in real-time via SocketIO.
3.  **Query** the game database using filters for name, price, and review score.
4.  **View** interactive dashboards (Plotly) generated from the filtered data.

This project is the evolution of a previous script (`mineracao-steam-mysql`), refactoring it into a user-friendly UI/UX tool for non-technical users.

## 🛠️ Tech Stack

* **Backend:** Flask, Flask-SocketIO
* **Data Collection:** Selenium, BeautifulSoup4
* **Database:** MySQL (communication via SQLAlchemy, PyMySQL)
* **Frontend/Visualization:** HTML, CSS, JavaScript (Socket.IO client), Plotly
* **Data Handling:** Pandas

## 🌟 Key Features

* **One-Click Mining:** Users can trigger the entire collection and storage pipeline via a button in the UI.
* **Real-Time Logging:** The interface displays the mining process status in real-time.
* **Dynamic Filtering:** The results page allows for complex queries to the database.
* **Interactive Dashboards:** Plotly charts are fully interactive, supporting zoom and hover-over details.

## 🚀 How to Run Locally

1.  **Clone the repo:** `git clone https://github.com/Gui-San/flask-steam-dashboard.git`
2.  **Create a venv:** `python -m venv venv`
3.  **Install dependencies:** `pip install -r requirements.txt`
4.  **Set up DB:** Configure your MySQL credentials in `app.py` and `pipeline.py`.
5.  **Run the app:** `python app.py`
6.  Open your browser to: `http://127.0.0.1:5000`
