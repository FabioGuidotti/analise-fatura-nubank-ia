import streamlit as st
import pandas as pd
from database import obter_categorias, adicionar_categoria, excluir_categoria, atualizar_categoria

def tela_gerenciar_categorias():

    usuario_id = st.session_state.user.id
    
    st.title("Gerenciar Categorias")

    # Exibir categorias existentes
    categorias = obter_categorias(usuario_id)
    st.write("Categorias existentes:", ", ".join(categorias))

    # Adicionar nova categoria
    nova_categoria = st.text_input("Nova categoria:")
    if st.button("Adicionar Categoria"):
        if nova_categoria:
            if adicionar_categoria(nova_categoria, usuario_id):
                st.success(f"Categoria '{nova_categoria}' adicionada com sucesso!")
            else:
                st.error(f"Não foi possível adicionar a categoria '{nova_categoria}'.")
        else:
            st.warning("Por favor, insira um nome para a nova categoria.")

    # Excluir categoria
    categoria_para_excluir = st.selectbox("Selecione a categoria para excluir:", categorias)
    if st.button("Excluir Categoria"):
        excluir_categoria(categoria_para_excluir, usuario_id)
        st.success(f"Categoria '{categoria_para_excluir}' excluída com sucesso!")

    # Atualizar categoria
    categoria_antiga = st.selectbox("Selecione a categoria para atualizar:", categorias)
    nova_categoria = st.text_input("Novo nome da categoria:")
    if st.button("Atualizar Categoria"):
        if atualizar_categoria(categoria_antiga, nova_categoria, usuario_id):
            st.success(f"Categoria atualizada de '{categoria_antiga}' para '{nova_categoria}'!")
        else:
            st.error("Não foi possível atualizar a categoria.")