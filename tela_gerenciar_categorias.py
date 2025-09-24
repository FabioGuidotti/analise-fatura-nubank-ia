import streamlit as st
import pandas as pd
from database import obter_categorias, adicionar_categoria, excluir_categoria, atualizar_categoria, obter_categoria_com_exemplos, atualizar_exemplos_categoria

def tela_gerenciar_categorias():

    usuario_id = st.session_state.user.id
    
    st.title("Gerenciar Categorias")

    # Exibir categorias existentes com exemplos
    categorias_com_exemplos = obter_categoria_com_exemplos(usuario_id)
    st.write("### Categorias Existentes")
    
    if categorias_com_exemplos:
        for cat in categorias_com_exemplos:
            exemplos_texto = f" (Exemplos: {cat['exemplos']})" if cat['exemplos'] else " (Sem exemplos)"
            st.write(f"• **{cat['nome']}**{exemplos_texto}")
    else:
        st.write("Nenhuma categoria cadastrada.")

    # Criar abas para diferentes operações
    tab1, tab2, tab3, tab4 = st.tabs(["Adicionar Categoria", "Excluir Categoria", "Atualizar Categoria", "Gerenciar Exemplos"])

    with tab1:
        st.subheader("Adicionar Nova Categoria")
        nova_categoria = st.text_input("Nome da nova categoria:")
        exemplos_nova = st.text_area("Exemplos de gastos (opcional):", 
                                   placeholder="Ex: Supermercado, Padaria, Açougue, Hortifruti...")
        
        if st.button("Adicionar Categoria"):
            if nova_categoria:
                if adicionar_categoria(nova_categoria, usuario_id):
                    # Se a categoria foi criada e há exemplos, atualizar os exemplos
                    if exemplos_nova.strip():
                        atualizar_exemplos_categoria(nova_categoria, exemplos_nova.strip(), usuario_id)
                    st.success(f"Categoria '{nova_categoria}' adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Não foi possível adicionar a categoria '{nova_categoria}'.")
            else:
                st.warning("Por favor, insira um nome para a nova categoria.")

    with tab2:
        st.subheader("Excluir Categoria")
        if categorias_com_exemplos:
            categoria_para_excluir = st.selectbox("Selecione a categoria para excluir:", 
                                                [cat['nome'] for cat in categorias_com_exemplos])
            if st.button("Excluir Categoria"):
                excluir_categoria(categoria_para_excluir, usuario_id)
                st.success(f"Categoria '{categoria_para_excluir}' excluída com sucesso!")
                st.rerun()
        else:
            st.write("Nenhuma categoria disponível para exclusão.")

    with tab3:
        st.subheader("Atualizar Nome da Categoria")
        if categorias_com_exemplos:
            categoria_antiga = st.selectbox("Selecione a categoria para atualizar:", 
                                          [cat['nome'] for cat in categorias_com_exemplos])
            nova_categoria = st.text_input("Novo nome da categoria:")
            if st.button("Atualizar Categoria"):
                if atualizar_categoria(categoria_antiga, nova_categoria, usuario_id):
                    st.success(f"Categoria atualizada de '{categoria_antiga}' para '{nova_categoria}'!")
                    st.rerun()
                else:
                    st.error("Não foi possível atualizar a categoria.")
        else:
            st.write("Nenhuma categoria disponível para atualização.")

    with tab4:
        st.subheader("Gerenciar Exemplos de Categorias")
        if categorias_com_exemplos:
            categoria_para_exemplos = st.selectbox("Selecione a categoria para gerenciar exemplos:", 
                                                  [cat['nome'] for cat in categorias_com_exemplos])
            
            # Encontrar a categoria selecionada
            categoria_selecionada = next((cat for cat in categorias_com_exemplos if cat['nome'] == categoria_para_exemplos), None)
            
            if categoria_selecionada:
                exemplos_atuais = categoria_selecionada['exemplos'] or ""
                exemplos_editados = st.text_area("Exemplos de gastos para esta categoria:", 
                                               value=exemplos_atuais,
                                               placeholder="Ex: Supermercado, Padaria, Açougue, Hortifruti...",
                                               help="Digite exemplos separados por vírgula ou quebra de linha")
                
                if st.button("Salvar Exemplos"):
                    if atualizar_exemplos_categoria(categoria_para_exemplos, exemplos_editados.strip(), usuario_id):
                        st.success(f"Exemplos da categoria '{categoria_para_exemplos}' atualizados com sucesso!")
                        st.rerun()
                    else:
                        st.error("Não foi possível atualizar os exemplos da categoria.")
        else:
            st.write("Nenhuma categoria disponível para gerenciar exemplos.")