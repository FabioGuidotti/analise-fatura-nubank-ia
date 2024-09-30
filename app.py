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
    
    # Estilo personalizado para a barra lateral
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .sidebar .sidebar-content .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
            border: none;
            border-radius: 0;
            padding: 15px 10px;
            text-align: left;
            background-color: transparent;
            color: #262730;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #e0e2e6;
        }
        .stButton>button:focus {
            background-color: #d0d2d6;
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