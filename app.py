import streamlit as st
import pandas as pd
from database import (
    run_migrations, salvar_dados, carregar_dados, excluir_transacao,
    obter_datas_faturas, excluir_transacoes_por_data,
    obter_arquivos_origem, excluir_transacoes_por_arquivo,
    obter_categorias, adicionar_categoria, excluir_categoria, atualizar_categoria
)
from ai_utils import extrair_transacoes_com_ai, conversar_com_ai
from data_processing import importar_fatura_nubank_pdf
from visualizations import criar_graficos_analise

st.set_page_config(layout="wide")

def main():
    run_migrations()

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

    # Inicializar a variável de seleção com "Análises"
    if 'selected' not in st.session_state:
        st.session_state.selected = "Análises"

    # Barra lateral
    with st.sidebar:
        # Tente carregar o logo centralizado
        try:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.image("logo.png", width=100, use_column_width=True)
        except:
            st.title("Gestão Financeira")
        
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

    # Conteúdo principal
    if st.session_state.selected == "Análises":
        analises()
    elif st.session_state.selected == "Conversar com IA":
        conversar_com_ia()
    elif st.session_state.selected == "Importar Fatura":
        importar_fatura()
    elif st.session_state.selected == "Visualizar e Gerenciar Dados":
        visualizar_e_gerenciar_dados()
    elif st.session_state.selected == "Gerenciar Categorias":
        gerenciar_categorias()

def importar_fatura():
    st.subheader("Importação da Fatura")
    faturas = st.file_uploader("Importar fatura(s) do cartão Nubank (PDF)", type=["pdf"], accept_multiple_files=True)
    if faturas:
        for fatura in faturas:
            novos_dados_fatura = importar_fatura_nubank_pdf(fatura)
            if novos_dados_fatura is not None:
                salvar_dados(novos_dados_fatura, fatura.name)
                st.success(f"Fatura {fatura.name} importada e salva com sucesso!")
            else:
                st.error(f"Falha ao importar a fatura {fatura.name}. Verifique o formato do arquivo ou o conteúdo da fatura.")
        st.success("Todas as faturas foram processadas!")

def visualizar_e_gerenciar_dados():
    st.subheader("Visualização e Gerenciamento dos Dados da Fatura")
    dados_fatura = carregar_dados()
    if not dados_fatura.empty:
        # Verificar e ajustar os nomes das colunas
        colunas = dados_fatura.columns
        coluna_valor = 'Valor' if 'Valor' in colunas else 'valor'
        coluna_data = 'Data' if 'Data' in colunas else 'data'
        coluna_descricao = 'Descrição' if 'Descrição' in colunas else 'descricao'
        coluna_categoria = 'Categoria' if 'Categoria' in colunas else 'categoria'
        coluna_arquivo = 'Arquivo de Origem' if 'Arquivo de Origem' in colunas else 'arquivo_origem'

        # Adicionar coluna de checkbox para exclusão
        dados_fatura['Excluir'] = False

        # Opções de ordenação
        colunas_ordenacao = [coluna_data, coluna_descricao, coluna_valor, coluna_categoria, coluna_arquivo]
        coluna_ordenacao = st.selectbox("Ordenar por:", colunas_ordenacao)
        ordem = st.radio("Ordem:", ["Crescente", "Decrescente"])

        # Ordenar o DataFrame
        if ordem == "Crescente":
            dados_fatura = dados_fatura.sort_values(by=coluna_ordenacao)
        else:
            dados_fatura = dados_fatura.sort_values(by=coluna_ordenacao, ascending=False)

        # Exibir o DataFrame com checkboxes editáveis
        dados_editados = st.data_editor(
            dados_fatura,
            hide_index=True,
            column_config={
                "Excluir": st.column_config.CheckboxColumn(
                    "Excluir",
                    help="Selecione para excluir a transação",
                    default=False,
                ),
                coluna_data: st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                coluna_valor: st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            },
            disabled=["id", coluna_data, coluna_descricao, coluna_valor, coluna_categoria, coluna_arquivo],
            num_rows="dynamic"
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="Download da fatura como CSV",
                data=dados_fatura.to_csv(index=False),
                file_name="fatura_nubank.csv",
                mime="text/csv",
            )
        with col2:
            if st.button("Excluir Transações Selecionadas"):
                transacoes_para_excluir = dados_editados[dados_editados['Excluir']]['id'].tolist()
                if transacoes_para_excluir:
                    for id_transacao in transacoes_para_excluir:
                        excluir_transacao(id_transacao)
                    st.success(f"{len(transacoes_para_excluir)} transação(ões) excluída(s) com sucesso!")
                    st.experimental_rerun()
                else:
                    st.warning("Nenhuma transação selecionada para exclusão.")
        with col3:
            if st.button("Limpar todos os dados"):
                conn = sqlite3.connect('fatura_nubank.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transacoes")
                conn.commit()
                conn.close()
                st.success("Todos os dados foram removidos do banco de dados!")
                st.experimental_rerun()

        # Gerenciamento de importações
        st.subheader("Excluir Faturas Completas")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("Excluir por data:")
            datas_faturas = obter_datas_faturas()
            fatura_para_excluir_data = st.selectbox("Selecione a fatura que deseja excluir (por data):", datas_faturas)
            if st.button("Excluir Fatura Selecionada (por data)"):
                excluir_transacoes_por_data(fatura_para_excluir_data)
                st.success(f"Todas as transações da fatura de {fatura_para_excluir_data} foram excluídas com sucesso!")
                st.experimental_rerun()
        
        with col2:
            st.write("Excluir por arquivo de origem:")
            arquivos_origem = obter_arquivos_origem()
            fatura_para_excluir_arquivo = st.selectbox("Selecione a fatura que deseja excluir (por arquivo):", arquivos_origem)
            if st.button("Excluir Fatura Selecionada (por arquivo)"):
                excluir_transacoes_por_arquivo(fatura_para_excluir_arquivo)
                st.success(f"Todas as transações do arquivo {fatura_para_excluir_arquivo} foram excluídas com sucesso!")
                st.experimental_rerun()

    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")

def analises():
    st.subheader("Análises da Fatura")
    dados_fatura = carregar_dados()
    if not dados_fatura.empty:
        criar_graficos_analise(dados_fatura)
    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")

def gerenciar_categorias():
    st.subheader("Gerenciar Categorias")
    
    # Carregar categorias existentes
    categorias = obter_categorias()
    
    # Criar um DataFrame com as categorias
    df_categorias = pd.DataFrame({"Categoria": categorias})
    
    # Adicionar uma linha vazia para nova categoria
    df_categorias = pd.concat([df_categorias, pd.DataFrame({"Categoria": [""]})], ignore_index=True)
    
    # Criar uma tabela editável
    edited_df = st.data_editor(
        df_categorias,
        column_config={
            "Categoria": st.column_config.TextColumn("Categoria", width="medium"),
            "Ações": st.column_config.Column(
                "Ações",
                width="medium",
                help="Ações para cada categoria"
            )
        },
        hide_index=True,
        num_rows="dynamic"
    )
    
    # Processar as alterações
    if st.button("Salvar Alterações"):
        novas_categorias = edited_df["Categoria"].dropna().tolist()
        categorias_atuais = set(categorias)
        novas_categorias_set = set(novas_categorias)
        
        # Adicionar novas categorias
        for categoria in novas_categorias_set - categorias_atuais:
            adicionar_categoria(categoria)
            st.success(f"Categoria '{categoria}' adicionada com sucesso!")
        
        # Remover categorias excluídas
        for categoria in categorias_atuais - novas_categorias_set:
            excluir_categoria(categoria)
            st.success(f"Categoria '{categoria}' excluída com sucesso!")
        
        # Atualizar categorias editadas
        for old_cat, new_cat in zip(categorias, novas_categorias):
            if old_cat != new_cat and old_cat in categorias_atuais and new_cat in novas_categorias_set:
                atualizar_categoria(old_cat, new_cat)
                st.success(f"Categoria atualizada de '{old_cat}' para '{new_cat}'!")
        
        st.experimental_rerun()

def conversar_com_ia():
    st.subheader("Conversar com IA sobre a Fatura")
    dados_fatura = carregar_dados()
    if not dados_fatura.empty:
        st.write("Faça perguntas sobre sua fatura e obtenha insights da IA.")
        
        # Área para exibir o histórico da conversa
        if "mensagens" not in st.session_state:
            st.session_state.mensagens = []

        for mensagem in st.session_state.mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])

        # Campo de entrada para a pergunta do usuário
        pergunta = st.chat_input("Faça uma pergunta sobre sua fatura:")

        if pergunta:
            # Adicionar a pergunta do usuário ao histórico
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            with st.chat_message("user"):
                st.markdown(pergunta)

            # Gerar e exibir a resposta da IA em streaming
            with st.chat_message("assistant"):
                resposta_placeholder = st.empty()
                resposta_completa = ""
                for chunk in conversar_com_ai(pergunta, dados_fatura):
                    if chunk.choices[0].delta.content is not None:
                        resposta_completa += chunk.choices[0].delta.content
                        resposta_placeholder.markdown(resposta_completa + "▌")
                resposta_placeholder.markdown(resposta_completa)

            # Adicionar a resposta completa ao histórico
            st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})

        # Botão para limpar o histórico da conversa
        if st.button("Limpar Conversa"):
            st.session_state.mensagens = []
            st.experimental_rerun()

    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")

if __name__ == "__main__":
    main()