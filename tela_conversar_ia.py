import streamlit as st
from database import carregar_dados
from ai_utils import conversar_com_ai

def tela_conversar_ia():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id
    
    dados_fatura = carregar_dados(usuario_id)
    if not dados_fatura.empty:  # Corrigido aqui
        st.write("Faça perguntas sobre sua fatura e obtenha insights da IA.")
        
        if "mensagens" not in st.session_state:
            st.session_state.mensagens = []

        for mensagem in st.session_state.mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])

        pergunta = st.chat_input("Faça uma pergunta sobre sua fatura:")

        if pergunta:
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            with st.chat_message("user"):
                st.markdown(pergunta)

            with st.chat_message("assistant"):
                resposta_placeholder = st.empty()
                resposta_completa = ""
                for chunk in conversar_com_ai(pergunta, dados_fatura):
                    if chunk.choices[0].delta.content is not None:
                        resposta_completa += chunk.choices[0].delta.content
                        resposta_placeholder.markdown(resposta_completa + "▌")
                resposta_placeholder.markdown(resposta_completa)

            st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})

        if st.button("Limpar Conversa"):
            st.session_state.mensagens = []
            st.rerun()
    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")