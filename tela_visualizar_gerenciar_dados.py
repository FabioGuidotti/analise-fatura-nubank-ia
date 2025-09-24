import streamlit as st
import pandas as pd
from database import (
    carregar_dados, excluir_transacao, obter_datas_faturas, 
    excluir_transacoes_por_data, obter_arquivos_origem, 
    excluir_transacoes_por_arquivo, limpar_todos_dados,
    atualizar_transacao, obter_categorias
)

def tela_visualizar_gerenciar_dados():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id

    st.title("📊 Gerenciamento de Dados")
    st.markdown("Visualize, edite e gerencie suas transações financeiras")

    dados_fatura = carregar_dados(usuario_id)
    
    if not dados_fatura.empty:
        # Estatísticas gerais
        st.subheader("📈 Resumo Geral")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Transações", len(dados_fatura))
        with col2:
            st.metric("Valor Total", f"R$ {dados_fatura['Valor'].sum():,.2f}")
        with col3:
            st.metric("Valor Médio", f"R$ {dados_fatura['Valor'].mean():,.2f}")
        with col4:
            st.metric("Maior Gasto", f"R$ {dados_fatura['Valor'].max():,.2f}")

        # Filtros e controles
        st.subheader("🔍 Filtros e Controles")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro por período
            if 'Data' in dados_fatura.columns:
                dados_fatura['Data'] = pd.to_datetime(dados_fatura['Data'])
                data_min = dados_fatura['Data'].min().date()
                data_max = dados_fatura['Data'].max().date()
                
                periodo = st.date_input(
                    "Período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    help="Filtrar por período"
                )
        
        with col2:
            # Filtro por categoria
            categorias = ['Todas'] + sorted(dados_fatura['Categoria'].unique().tolist())
            categoria_filtro = st.selectbox("Categoria", categorias)
        
        with col3:
            # Filtro por valor
            valor_min = st.number_input("Valor Mínimo (R$)", min_value=0.0, value=0.0, step=0.01)
        
        with col4:
            # Filtro por arquivo
            arquivos = ['Todos'] + sorted(dados_fatura['Arquivo de Origem'].unique().tolist())
            arquivo_filtro = st.selectbox("Arquivo", arquivos)

        # Aplicar filtros
        dados_filtrados = dados_fatura.copy()
        
        if isinstance(periodo, tuple) and len(periodo) == 2:
            dados_filtrados = dados_filtrados[
                (dados_filtrados['Data'].dt.date >= periodo[0]) & 
                (dados_filtrados['Data'].dt.date <= periodo[1])
            ]
        
        if categoria_filtro != 'Todas':
            dados_filtrados = dados_filtrados[dados_filtrados['Categoria'] == categoria_filtro]
        
        dados_filtrados = dados_filtrados[dados_filtrados['Valor'] >= valor_min]
        
        if arquivo_filtro != 'Todos':
            dados_filtrados = dados_filtrados[dados_filtrados['Arquivo de Origem'] == arquivo_filtro]

        st.info(f"📊 Mostrando {len(dados_filtrados)} de {len(dados_fatura)} transações")

        # Ordenação
        col1, col2 = st.columns(2)
        with col1:
            coluna_ordenacao = st.selectbox(
                "Ordenar por:",
                ['Data', 'Descrição', 'Valor', 'Categoria', 'Arquivo de Origem']
            )
        with col2:
            ordem = st.radio("Ordem:", ["Crescente", "Decrescente"], horizontal=True)

        if ordem == "Crescente":
            dados_filtrados = dados_filtrados.sort_values(by=coluna_ordenacao)
        else:
            dados_filtrados = dados_filtrados.sort_values(by=coluna_ordenacao, ascending=False)

        # Tabela de dados editável
        st.subheader("📋 Dados das Transações")
        
        # Obter categorias disponíveis para edição
        categorias_disponiveis = obter_categorias(usuario_id)
        opcoes_categorias = categorias_disponiveis if categorias_disponiveis else ['Outros']

        dados_editados = st.data_editor(
            dados_filtrados,
            hide_index=True,
            column_config={
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f", step=0.01),
                "Descrição": st.column_config.TextColumn("Descrição", max_chars=100),
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=opcoes_categorias,
                    help="Selecione a categoria"
                ),
                "Arquivo de Origem": st.column_config.TextColumn("Arquivo", disabled=True),
            },
            disabled=["id", "Arquivo de Origem"],
            num_rows="dynamic",
            use_container_width=True
        )

        # Botões de ação
        st.subheader("⚡ Ações")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Salvar Alterações", type="primary"):
                # Verificar se há alterações
                if not dados_editados.equals(dados_filtrados):
                    try:
                        # Atualizar cada transação modificada
                        alteracoes = 0
                        for idx, row in dados_editados.iterrows():
                            if idx in dados_filtrados.index:
                                original = dados_filtrados.loc[idx]
                                if not row.equals(original):
                                    atualizar_transacao(
                                        row['id'],
                                        row['Data'],
                                        row['Descrição'],
                                        row['Valor'],
                                        row['Categoria'],
                                        usuario_id
                                    )
                                    alteracoes += 1
                        
                        if alteracoes > 0:
                            st.success(f"✅ {alteracoes} transação(ões) atualizada(s) com sucesso!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Nenhuma alteração detectada.")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar alterações: {str(e)}")
                else:
                    st.info("ℹ️ Nenhuma alteração detectada.")
        
        with col2:
            if st.button("📥 Exportar CSV"):
                csv = dados_filtrados.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"dados_filtrados_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("🗑️ Excluir Selecionadas"):
                # Implementar seleção múltipla
                st.warning("Funcionalidade de exclusão em desenvolvimento")
        
        with col4:
            if st.button("🔄 Atualizar Dados"):
                st.rerun()

        # Seção de exclusão em massa
        st.subheader("🗂️ Exclusão em Massa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Excluir por Data:**")
            datas_faturas = obter_datas_faturas(usuario_id)
            if datas_faturas:
                fatura_data = st.selectbox("Selecione a data:", datas_faturas, key="excluir_data")
                if st.button("🗑️ Excluir por Data", key="btn_excluir_data"):
                    if excluir_transacoes_por_data(fatura_data, usuario_id):
                        st.success(f"✅ Fatura de {fatura_data} excluída com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir fatura por data.")
            else:
                st.info("Nenhuma fatura disponível para exclusão por data.")
        
        with col2:
            st.write("**Excluir por Arquivo:**")
            arquivos_origem = obter_arquivos_origem(usuario_id)
            if arquivos_origem:
                fatura_arquivo = st.selectbox("Selecione o arquivo:", arquivos_origem, key="excluir_arquivo")
                if st.button("🗑️ Excluir por Arquivo", key="btn_excluir_arquivo"):
                    if excluir_transacoes_por_arquivo(fatura_arquivo, usuario_id):
                        st.success(f"✅ Arquivo {fatura_arquivo} excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir arquivo.")
            else:
                st.info("Nenhum arquivo disponível para exclusão.")

        # Ação perigosa
        st.subheader("⚠️ Ações Avançadas")
        
        with st.expander("🚨 Limpar Todos os Dados", expanded=False):
            st.warning("⚠️ Esta ação irá remover TODOS os dados do banco. Esta ação não pode ser desfeita!")
            
            col1, col2 = st.columns(2)
            with col1:
                confirmar = st.checkbox("Confirmo que quero excluir todos os dados")
            with col2:
                if st.button("🗑️ Limpar Tudo", disabled=not confirmar, type="secondary"):
                    if limpar_todos_dados(usuario_id):
                        st.success("✅ Todos os dados foram removidos!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao limpar dados.")

    else:
        st.warning("📭 Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")
        
        # Sugestões para o usuário
        st.info("💡 **Dicas:**\n"
                "- Use a tela 'Importar Fatura' para adicionar dados\n"
                "- Suas transações aparecerão aqui após a importação\n"
                "- Você poderá editar, filtrar e gerenciar seus dados")