import streamlit as st
from database import testar_conexao
from tela_analises import tela_analises
from tela_conversar_ia import tela_conversar_ia
from tela_importar_fatura import tela_importar_fatura
from tela_visualizar_gerenciar_dados import tela_visualizar_gerenciar_dados
from tela_gerenciar_categorias import tela_gerenciar_categorias
from tela_login import tela_login, tela_registro
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

st.set_page_config(layout="wide")

def main():
    if not testar_conexao():
        st.error("Não foi possível conectar ao banco de dados. Verifique as configurações de conexão.")
        return
    
    # Estilos personalizados para tema escuro e mobile
    st.markdown(
        """
        <style>
        /* Estilo da sidebar */
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .sidebar .sidebar-content .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Botões da sidebar - melhorados para mobile e tema escuro */
        .stButton>button {
            width: 100%;
            border: 2px solid #e0e0e0;
            border-radius: 0.5rem;
            padding: 15px 10px;
            text-align: left;
            background-color: white;
            color: #262730;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 4px 0;
        }
        
        .stButton>button:hover {
            background-color: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(255,75,75,0.3);
        }
        
        .stButton>button:focus {
            background-color: #ff4b4b;
            color: white;
            border-color: #ff4b4b;
            box-shadow: 0 0 0 3px rgba(255,75,75,0.2);
        }
        
        /* Melhorias para mobile */
        @media (max-width: 768px) {
            .stButton>button {
                min-height: 48px;
                font-size: 16px;
                padding: 16px 12px;
                margin: 6px 0;
                border-radius: 0.75rem;
            }
            
            /* Melhor contraste para texto */
            .stButton>button {
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
        }
        
        /* Melhorias para tema escuro */
        @media (prefers-color-scheme: dark) {
            .sidebar .sidebar-content {
                background-color: #1e1e1e;
            }
            
            .stButton>button {
                background-color: #2d2d2d;
                color: #ffffff;
                border-color: #404040;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            
            .stButton>button:hover {
                background-color: #ff4b4b;
                color: white;
                border-color: #ff4b4b;
                box-shadow: 0 4px 12px rgba(255,75,75,0.4);
            }
            
            .stButton>button:focus {
                background-color: #ff4b4b;
                color: white;
                border-color: #ff4b4b;
                box-shadow: 0 0 0 3px rgba(255,75,75,0.3);
            }
        }
        
        /* Melhorias para botões em outras telas */
        .main .stButton > button {
            background-color: #ff4b4b !important;
            color: white !important;
            border: 2px solid #ff4b4b !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            padding: 12px 24px !important;
        }
        
        .main .stButton > button:hover {
            background-color: #ff6b6b !important;
            border-color: #ff6b6b !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        
        .main .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Botões secundários */
        .main .stButton > button[kind="secondary"] {
            background-color: #6c757d !important;
            border-color: #6c757d !important;
        }
        
        .main .stButton > button[kind="secondary"]:hover {
            background-color: #5a6268 !important;
            border-color: #5a6268 !important;
        }
        
        /* Botões de sucesso */
        .main .stButton > button[kind="primary"] {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
        }
        
        .main .stButton > button[kind="primary"]:hover {
            background-color: #218838 !important;
            border-color: #218838 !important;
        }
        
        /* Melhorias para mobile - botões principais */
        @media (max-width: 768px) {
            .main .stButton > button {
                min-height: 44px !important;
                font-size: 16px !important;
                padding: 12px 24px !important;
                margin: 4px 0 !important;
                width: 100% !important;
            }
            
            /* Botões em colunas no mobile */
            .main .stButton {
                width: 100% !important;
                margin: 4px 0 !important;
            }
        }
        
        /* Melhorias para tema escuro - botões principais */
        @media (prefers-color-scheme: dark) {
            .main .stButton > button {
                background-color: #ff4b4b !important;
                color: white !important;
                border: 2px solid #ff4b4b !important;
                box-shadow: 0 2px 8px rgba(255,75,75,0.3) !important;
            }
            
            .main .stButton > button:hover {
                background-color: #ff6b6b !important;
                border-color: #ff6b6b !important;
                box-shadow: 0 4px 12px rgba(255,75,75,0.4) !important;
            }
            
            .main .stButton > button[kind="secondary"] {
                background-color: #495057 !important;
                border-color: #495057 !important;
                box-shadow: 0 2px 8px rgba(73,80,87,0.3) !important;
            }
            
            .main .stButton > button[kind="secondary"]:hover {
                background-color: #343a40 !important;
                border-color: #343a40 !important;
                box-shadow: 0 4px 12px rgba(73,80,87,0.4) !important;
            }
            
            .main .stButton > button[kind="primary"] {
                background-color: #28a745 !important;
                border-color: #28a745 !important;
                box-shadow: 0 2px 8px rgba(40,167,69,0.3) !important;
            }
            
            .main .stButton > button[kind="primary"]:hover {
                background-color: #218838 !important;
                border-color: #218838 !important;
                box-shadow: 0 4px 12px rgba(40,167,69,0.4) !important;
            }
        }
        
        /* Melhorias para selectbox e inputs */
        .stSelectbox > div > div {
            background-color: white !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #ff4b4b !important;
        }
        
        .stNumberInput > div > div > input {
            background-color: white !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
        }
        
        .stNumberInput > div > div > input:focus {
            border-color: #ff4b4b !important;
            box-shadow: 0 0 0 3px rgba(255,75,75,0.1) !important;
        }
        
        /* Melhorias para data input */
        .stDateInput > div > div > input {
            background-color: white !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
        }
        
        .stDateInput > div > div > input:focus {
            border-color: #ff4b4b !important;
            box-shadow: 0 0 0 3px rgba(255,75,75,0.1) !important;
        }
        
        /* Melhorias para expanders */
        .streamlit-expanderHeader {
            background-color: #f8f9fa !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
        }
        
        .streamlit-expanderContent {
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
            border-top: none !important;
            border-radius: 0 0 0.5rem 0.5rem !important;
        }
        
        /* Melhorias para métricas */
        .metric-container {
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
            padding: 1rem !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Melhorias para tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f8f9fa !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border-color: #ff4b4b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Inicializar variáveis de sessão
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'selected' not in st.session_state:
        st.session_state.selected = "Análises"

    # Verificar autenticação
    if not st.session_state.authenticated:
        if st.session_state.show_register:
            tela_registro()
        else:
            tela_login()
        return

    # Barra lateral
    with st.sidebar:
        try:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image("logo.png", width=100, use_column_width=True)
        except:
            st.title("Gestão Financeira")
        
        st.write(f"Bem-vindo, {st.session_state.user.name}!")
        
        # Menu reordenado
        if st.button("📈 Análises"):
            st.session_state.selected = "Análises"
        if st.button("🤖 Conversar com IA"):
            st.session_state.selected = "Conversar com IA"
        if st.button("📁 Importar Fatura"):
            st.session_state.selected = "Importar Fatura"
        if st.button("📊 Visualizar e Gerenciar Dados"):
            st.session_state.selected = "Visualizar e Gerenciar Dados"
        if st.button("🏷️ Gerenciar Categorias"):
            st.session_state.selected = "Gerenciar Categorias"
        
        if st.button("Sair"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()  # Substitua st.experimental_rerun() por st.rerun()

    # Conteúdo principal
    if st.session_state.selected == "Análises":
        tela_analises()
    elif st.session_state.selected == "Conversar com IA":
        tela_conversar_ia()
    elif st.session_state.selected == "Importar Fatura":
        tela_importar_fatura()
    elif st.session_state.selected == "Visualizar e Gerenciar Dados":
        tela_visualizar_gerenciar_dados()
    elif st.session_state.selected == "Gerenciar Categorias":
        tela_gerenciar_categorias()

if __name__ == "__main__":
    main()