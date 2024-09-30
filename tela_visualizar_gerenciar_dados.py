import streamlit as st
from database import carregar_dados, excluir_transacao, obter_datas_faturas, excluir_transacoes_por_data, obter_arquivos_origem, excluir_transacoes_por_arquivo, limpar_todos_dados

def tela_visualizar_gerenciar_dados():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id

    st.subheader("Visualização e Gerenciamento dos Dados da Fatura")
    dados_fatura = carregar_dados(usuario_id)
    if not dados_fatura.empty:
        colunas = dados_fatura.columns
        coluna_valor = 'Valor' if 'Valor' in colunas else 'valor'
        coluna_data = 'Data' if 'Data' in colunas else 'data'
        coluna_descricao = 'Descrição' if 'Descrição' in colunas else 'descricao'
        coluna_categoria = 'Categoria' if 'Categoria' in colunas else 'categoria'
        coluna_arquivo = 'Arquivo de Origem' if 'Arquivo de Origem' in colunas else 'arquivo_origem'

        dados_fatura['Excluir'] = False

        colunas_ordenacao = [coluna_data, coluna_descricao, coluna_valor, coluna_categoria, coluna_arquivo]
        coluna_ordenacao = st.selectbox("Ordenar por:", colunas_ordenacao)
        ordem = st.radio("Ordem:", ["Crescente", "Decrescente"])

        if ordem == "Crescente":
            dados_fatura = dados_fatura.sort_values(by=coluna_ordenacao)
        else:
            dados_fatura = dados_fatura.sort_values(by=coluna_ordenacao, ascending=False)

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
                        excluir_transacao(id_transacao, usuario_id)
                    st.success(f"{len(transacoes_para_excluir)} transação(ões) excluída(s) com sucesso!")
                    st.rerun()
                else:
                    st.warning("Nenhuma transação selecionada para exclusão.")
        with col3:
            if st.button("Limpar todos os dados"):
                if limpar_todos_dados(usuario_id):
                    st.success("Todos os dados foram removidos do banco de dados!")
                    st.rerun()
                else:
                    st.error("Ocorreu um erro ao tentar limpar os dados.")

        st.subheader("Excluir Faturas Completas")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("Excluir por data:")
            datas_faturas = obter_datas_faturas(usuario_id)
            fatura_para_excluir_data = st.selectbox("Selecione a fatura que deseja excluir (por data):", datas_faturas)
            if st.button("Excluir Fatura Selecionada (por data)"):
                excluir_transacoes_por_data(fatura_para_excluir_data, usuario_id)
                st.success(f"Todas as transações da fatura de {fatura_para_excluir_data} foram excluídas com sucesso!")
                st.rerun()
        
        with col2:
            st.write("Excluir por arquivo de origem:")
            arquivos_origem = obter_arquivos_origem(usuario_id)
            fatura_para_excluir_arquivo = st.selectbox("Selecione a fatura que deseja excluir (por arquivo):", arquivos_origem)
            if st.button("Excluir Fatura Selecionada (por arquivo)"):
                excluir_transacoes_por_arquivo(fatura_para_excluir_arquivo, usuario_id)
                st.success(f"Todas as transações do arquivo {fatura_para_excluir_arquivo} foram excluídas com sucesso!")
                st.rerun()

    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")