import streamlit as st
from database import Session, criar_usuario, autenticar_usuario, Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    session = Session()
    user = session.query(Usuario).filter(Usuario.name == username).first()
    session.close()
    if not user or not verify_password(password, user.senha):
        return None
    return user

def tela_login():
    st.title("Login")

    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Nome de usuário ou senha incorretos")

    st.markdown("---")
    st.write("Não tem uma conta?")
    if st.button("Registrar"):
        st.session_state.show_register = True
        st.rerun()

def tela_registro():
    st.title("Registro")

    username = st.text_input("Nome de usuário")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a senha", type="password")

    if st.button("Registrar"):
        if password != confirm_password:
            st.error("As senhas não coincidem")
        else:
            hashed_password = pwd_context.hash(password)
            user_id = criar_usuario(username, username, hashed_password)  # Usando o nome como email temporariamente
            if user_id:
                st.success("Usuário registrado com sucesso! Faça login para continuar.")
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error("Nome de usuário já existe")

    if st.button("Voltar para o login"):
        st.session_state.show_register = False
        st.rerun()