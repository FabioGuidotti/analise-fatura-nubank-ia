import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import carregar_dados, obter_datas_faturas, obter_arquivos_origem

def criar_graficos_analise(dados_fatura):
    # Verificar e ajustar os nomes das colunas
    colunas = dados_fatura.columns
    coluna_valor = 'Valor' if 'Valor' in colunas else 'valor'
    coluna_data = 'Data' if 'Data' in colunas else 'data'
    coluna_descricao = 'Descrição' if 'Descrição' in colunas else 'descricao'
    coluna_categoria = 'Categoria' if 'Categoria' in colunas else 'categoria'

    # Verificar se a coluna de data existe
    if coluna_data not in dados_fatura.columns:
        st.error(f"Coluna de data '{coluna_data}' não encontrada no DataFrame.")
        st.write("Colunas disponíveis:", dados_fatura.columns.tolist())
        return

    # Assegure-se de que a coluna de data está no formato correto
    if not pd.api.types.is_datetime64_any_dtype(dados_fatura[coluna_data]):
        dados_fatura[coluna_data] = pd.to_datetime(dados_fatura[coluna_data], errors='coerce')
    
    # Gráficos de linha e barra lado a lado
    st.subheader("Evolução dos Gastos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de linha para gastos ao longo do tempo (por semana)
        dados_fatura['Semana'] = dados_fatura[coluna_data].dt.to_period('W').apply(lambda r: r.start_time)
        gastos_semanais = dados_fatura.groupby('Semana')[coluna_valor].sum().reset_index()
        fig_linha = px.line(gastos_semanais, x='Semana', y=coluna_valor, title='Gastos Semanais')
        fig_linha.update_traces(line_shape='spline', line_smoothing=0.6)
        fig_linha.update_layout(xaxis_title='Semana', yaxis_title='Valor Total (R$)')
        st.plotly_chart(fig_linha, use_container_width=True)

    with col2:
        # Gráfico de barras para gastos mensais
        dados_fatura['Mês'] = dados_fatura[coluna_data].dt.to_period('M').apply(lambda r: r.start_time)
        gastos_mensais = dados_fatura.groupby('Mês')[coluna_valor].sum().reset_index()
        fig_mensal = px.bar(gastos_mensais, x='Mês', y=coluna_valor, title='Gastos Mensais')
        fig_mensal.update_layout(xaxis_title='Mês', yaxis_title='Valor Total (R$)')
        st.plotly_chart(fig_mensal, use_container_width=True)

    # Gráficos de pizza e barras horizontais lado a lado
    st.subheader("Distribuição dos Gastos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza para gastos por categoria
        gastos_por_categoria = dados_fatura.groupby(coluna_categoria)[coluna_valor].sum().reset_index()
        # Garantir que a categoria "Outros" seja exibida
        if "Outros" not in gastos_por_categoria[coluna_categoria].values:
            novo_registro = pd.DataFrame({coluna_categoria: ["Outros"], coluna_valor: [0]})
            gastos_por_categoria = pd.concat([gastos_por_categoria, novo_registro], ignore_index=True)
        fig_categoria = px.pie(gastos_por_categoria, 
                               values=coluna_valor, 
                               names=coluna_categoria, 
                               title='Gastos por Categoria',
                               hole=0.3)  # Adiciona um buraco no centro para melhor visualização
        fig_categoria.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_categoria, use_container_width=True)

    with col2:
        # Gráfico de barras horizontal para os maiores gastos
        top_gastos = dados_fatura.nlargest(10, coluna_valor)
        fig_top = px.bar(top_gastos, 
                         x=coluna_valor, 
                         y=coluna_descricao, 
                         orientation='h',
                         title='Top 10 Maiores Gastos',
                         labels={coluna_valor: 'Valor (R$)', coluna_descricao: ''},
                         text=coluna_valor)
        fig_top.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    # Gráficos de frequência e dia da semana lado a lado
    st.subheader("Padrões de Gastos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras para frequência de gastos
        freq_gastos = dados_fatura[coluna_descricao].value_counts().head(10)
        fig_freq = px.bar(x=freq_gastos.index, y=freq_gastos.values, title='Top 10 Gastos Mais Frequentes')
        fig_freq.update_xaxes(title='Descrição')
        fig_freq.update_yaxes(title='Frequência')
        st.plotly_chart(fig_freq, use_container_width=True)

    with col2:
        # Gráfico de barras para gastos por dia da semana
        dados_fatura['Dia da Semana'] = dados_fatura[coluna_data].dt.day_name()
        gastos_por_dia_semana = dados_fatura.groupby('Dia da Semana')[coluna_valor].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        fig_dia_semana = px.bar(x=gastos_por_dia_semana.index, y=gastos_por_dia_semana.values, title='Gastos por Dia da Semana')
        fig_dia_semana.update_xaxes(title='Dia da Semana')
        fig_dia_semana.update_yaxes(title='Valor Total')
        st.plotly_chart(fig_dia_semana, use_container_width=True)

def tela_analises():
    if 'user' not in st.session_state or not st.session_state.user:
        st.error("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id

    # Header principal
    st.title("📊 Análises Financeiras")
    st.markdown("Visualize insights detalhados sobre seus gastos e padrões financeiros")
    
    dados_fatura = carregar_dados(usuario_id)
    
    if not dados_fatura.empty:
        # Converter coluna de data se necessário
        if 'Data' in dados_fatura.columns:
            dados_fatura['Data'] = pd.to_datetime(dados_fatura['Data'])
        
        # Sidebar organizada
        with st.sidebar:
            # Header da sidebar
            st.markdown("## 🔍 Controles de Análise")
            st.markdown("---")
            
            # Seção de Filtros
            with st.expander("📊 Filtros de Dados", expanded=True):
                # Filtro por período
                st.markdown("**📅 Período**")
                data_min = dados_fatura['Data'].min().date()
                data_max = dados_fatura['Data'].max().date()
                
                periodo = st.date_input(
                    "Selecione o período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    help="Filtrar transações por período",
                    label_visibility="collapsed"
                )
                
                st.markdown("**🏷️ Categoria**")
                categorias = ['Todas'] + sorted(dados_fatura['Categoria'].unique().tolist())
                categoria_selecionada = st.selectbox(
                    "Escolha uma categoria",
                    categorias,
                    help="Filtrar por categoria específica",
                    label_visibility="collapsed"
                )
                
                st.markdown("**💰 Valor Mínimo**")
                valor_min = st.number_input(
                    "Valor em R$",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    help="Mostrar apenas gastos acima deste valor",
                    label_visibility="collapsed"
                )
                
                st.markdown("**📁 Arquivo de Origem**")
                arquivos = ['Todos'] + sorted(dados_fatura['Arquivo de Origem'].unique().tolist())
                arquivo_selecionado = st.selectbox(
                    "Selecione o arquivo",
                    arquivos,
                    help="Filtrar por arquivo de origem",
                    label_visibility="collapsed"
                )
            
            # Seção de Ações
            with st.expander("⚡ Ações Rápidas", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔄 Atualizar", help="Recarregar dados", use_container_width=True):
                        st.rerun()
                
                with col2:
                    if st.button("📊 Reset", help="Limpar filtros", use_container_width=True):
                        st.rerun()
                
                # Exportação
                st.markdown("**📥 Exportar Dados**")
                if st.button("💾 Download CSV", use_container_width=True):
                    # Aplicar filtros para exportação
                    dados_export = aplicar_filtros(dados_fatura, periodo, categoria_selecionada, valor_min, arquivo_selecionado)
                    csv = dados_export.to_csv(index=False)
                    st.download_button(
                        label="📁 Baixar CSV",
                        data=csv,
                        file_name=f"analise_financeira_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            # Seção de Informações
            with st.expander("ℹ️ Informações", expanded=False):
                st.markdown("**📈 Dados Atuais**")
                st.metric("Total de Transações", len(dados_fatura))
                st.metric("Valor Total", f"R$ {dados_fatura['Valor'].sum():,.2f}")
                
                st.markdown("**📅 Período dos Dados**")
                st.write(f"De: {data_min.strftime('%d/%m/%Y')}")
                st.write(f"Até: {data_max.strftime('%d/%m/%Y')}")
                
                st.markdown("**🏷️ Categorias Disponíveis**")
                for cat in sorted(dados_fatura['Categoria'].unique()):
                    count = len(dados_fatura[dados_fatura['Categoria'] == cat])
                    st.write(f"• {cat} ({count} transações)")
        
        # Aplicar filtros
        dados_filtrados = aplicar_filtros(dados_fatura, periodo, categoria_selecionada, valor_min, arquivo_selecionado)
        
        # Resumo dos filtros
        st.info(f"📊 **Mostrando {len(dados_filtrados)} de {len(dados_fatura)} transações**")
        
        if not dados_filtrados.empty:
            # Métricas principais
            st.subheader("📈 Resumo Executivo")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "Total de Transações", 
                    len(dados_filtrados),
                    delta=f"{len(dados_filtrados) - len(dados_fatura)}" if len(dados_filtrados) != len(dados_fatura) else None
                )
            
            with col2:
                valor_total = dados_filtrados['Valor'].sum()
                st.metric(
                    "Valor Total", 
                    f"R$ {valor_total:,.2f}",
                    delta=f"R$ {valor_total - dados_fatura['Valor'].sum():,.2f}" if len(dados_filtrados) != len(dados_fatura) else None
                )
            
            with col3:
                st.metric("Valor Médio", f"R$ {dados_filtrados['Valor'].mean():,.2f}")
            
            with col4:
                st.metric("Maior Gasto", f"R$ {dados_filtrados['Valor'].max():,.2f}")
            
            with col5:
                st.metric("Menor Gasto", f"R$ {dados_filtrados['Valor'].min():,.2f}")
            
            # Tabs para organizar as análises
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Gráficos", "📋 Tabelas", "🔍 Insights", "📈 Comparações"])
            
            with tab1:
                st.subheader("📊 Visualizações Gráficas")
                criar_graficos_analise(dados_filtrados)
            
            with tab2:
                st.subheader("📋 Dados Detalhados")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Maiores Gastos**")
                    maiores_gastos = dados_filtrados.nlargest(15, 'Valor')
                    st.dataframe(
                        maiores_gastos[['Data', 'Descrição', 'Valor', 'Categoria']],
                        use_container_width=True,
                        hide_index=True
                    )
                
                with col2:
                    st.write("**Resumo por Categoria**")
                    gastos_por_categoria = dados_filtrados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
                    
                    for categoria, valor in gastos_por_categoria.head(10).items():
                        percentual = (valor / gastos_por_categoria.sum()) * 100
                        st.metric(
                            categoria, 
                            f"R$ {valor:,.2f}",
                            f"{percentual:.1f}%"
                        )
            
            with tab3:
                st.subheader("🔍 Insights Automáticos")
                gerar_insights(dados_filtrados)
            
            with tab4:
                st.subheader("📈 Comparações Temporais")
                criar_comparacoes_temporais(dados_filtrados)
                
        else:
            st.warning("⚠️ Nenhuma transação encontrada com os filtros aplicados.")
            st.info("💡 Tente ajustar os filtros na barra lateral para ver mais dados.")
    else:
        st.warning("📭 Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")
        
        # Sugestões para o usuário
        st.info("💡 **Próximos passos:**\n"
                "- Use a tela 'Importar Fatura' para adicionar dados\n"
                "- Suas análises aparecerão aqui após a importação\n"
                "- Explore diferentes visualizações e insights")

def aplicar_filtros(dados_fatura, periodo, categoria_selecionada, valor_min, arquivo_selecionado):
    """Aplica os filtros selecionados aos dados"""
    dados_filtrados = dados_fatura.copy()
    
    # Filtro por período
    if isinstance(periodo, tuple) and len(periodo) == 2:
        dados_filtrados = dados_filtrados[
            (dados_filtrados['Data'].dt.date >= periodo[0]) & 
            (dados_filtrados['Data'].dt.date <= periodo[1])
        ]
    
    # Filtro por categoria
    if categoria_selecionada != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['Categoria'] == categoria_selecionada]
    
    # Filtro por valor mínimo
    dados_filtrados = dados_filtrados[dados_filtrados['Valor'] >= valor_min]
    
    # Filtro por arquivo
    if arquivo_selecionado != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['Arquivo de Origem'] == arquivo_selecionado]
    
    return dados_filtrados

def gerar_insights(dados_filtrados):
    """Gera insights automáticos sobre os dados"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Estatísticas Gerais**")
        
        # Categoria com maior gasto
        gastos_por_categoria = dados_filtrados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        categoria_maior = gastos_por_categoria.index[0]
        valor_maior = gastos_por_categoria.iloc[0]
        percentual_maior = (valor_maior / gastos_por_categoria.sum()) * 100
        
        st.success(f"🏆 **Categoria com maior gasto:** {categoria_maior} (R$ {valor_maior:,.2f} - {percentual_maior:.1f}%)")
        
        # Média de gastos por transação
        media_gastos = dados_filtrados['Valor'].mean()
        st.info(f"💰 **Gasto médio por transação:** R$ {media_gastos:,.2f}")
        
        # Frequência de compras
        dias_unicos = dados_filtrados['Data'].nunique()
        total_dias = (dados_filtrados['Data'].max() - dados_filtrados['Data'].min()).days + 1
        frequencia = len(dados_filtrados) / total_dias if total_dias > 0 else 0
        
        st.info(f"📅 **Frequência média:** {frequencia:.1f} transações por dia")
    
    with col2:
        st.write("**🔍 Padrões Identificados**")
        
        # Dia da semana com mais gastos
        dados_filtrados['Dia_Semana'] = dados_filtrados['Data'].dt.day_name()
        gastos_por_dia = dados_filtrados.groupby('Dia_Semana')['Valor'].sum().sort_values(ascending=False)
        dia_maior = gastos_por_dia.index[0]
        valor_dia = gastos_por_dia.iloc[0]
        
        st.success(f"📆 **Dia com mais gastos:** {dia_maior} (R$ {valor_dia:,.2f})")
        
        # Maior transação individual
        maior_transacao = dados_filtrados.loc[dados_filtrados['Valor'].idxmax()]
        st.info(f"💸 **Maior transação:** {maior_transacao['Descrição']} - R$ {maior_transacao['Valor']:,.2f}")
        
        # Estabelecimento mais frequente
        estabelecimento_freq = dados_filtrados['Descrição'].value_counts().head(1)
        if not estabelecimento_freq.empty:
            est_mais_freq = estabelecimento_freq.index[0]
            freq_count = estabelecimento_freq.iloc[0]
            st.info(f"🏪 **Estabelecimento mais frequente:** {est_mais_freq} ({freq_count} vezes)")

def criar_comparacoes_temporais(dados_filtrados):
    """Cria comparações temporais dos dados"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📈 Evolução Semanal**")
        
        # Gráfico de evolução semanal
        dados_filtrados['Semana'] = dados_filtrados['Data'].dt.to_period('W').apply(lambda r: r.start_time)
        gastos_semanais = dados_filtrados.groupby('Semana')['Valor'].sum().reset_index()
        
        fig_semanal = px.line(
            gastos_semanais, 
            x='Semana', 
            y='Valor', 
            title='Evolução dos Gastos Semanais',
            markers=True
        )
        fig_semanal.update_traces(line_shape='spline', line_smoothing=0.6)
        fig_semanal.update_layout(
            xaxis_title='Semana',
            yaxis_title='Valor Total (R$)',
            showlegend=False
        )
        st.plotly_chart(fig_semanal, use_container_width=True)
    
    with col2:
        st.write("**📊 Comparação Mensal**")
        
        # Gráfico de comparação mensal
        dados_filtrados['Mes'] = dados_filtrados['Data'].dt.to_period('M').apply(lambda r: r.start_time)
        gastos_mensais = dados_filtrados.groupby('Mes')['Valor'].sum().reset_index()
        
        fig_mensal = px.bar(
            gastos_mensais, 
            x='Mes', 
            y='Valor', 
            title='Gastos por Mês',
            color='Valor',
            color_continuous_scale='Blues'
        )
        fig_mensal.update_layout(
            xaxis_title='Mês',
            yaxis_title='Valor Total (R$)',
            showlegend=False
        )
        st.plotly_chart(fig_mensal, use_container_width=True)
    
    # Comparação de categorias ao longo do tempo
    st.write("**🏷️ Evolução por Categoria**")
    
    dados_filtrados['Mes'] = dados_filtrados['Data'].dt.to_period('M').apply(lambda r: r.start_time)
    gastos_categoria_mes = dados_filtrados.groupby(['Mes', 'Categoria'])['Valor'].sum().reset_index()
    
    fig_categoria_tempo = px.line(
        gastos_categoria_mes,
        x='Mes',
        y='Valor',
        color='Categoria',
        title='Evolução dos Gastos por Categoria',
        markers=True
    )
    fig_categoria_tempo.update_layout(
        xaxis_title='Mês',
        yaxis_title='Valor Total (R$)',
        legend_title='Categoria'
    )
    st.plotly_chart(fig_categoria_tempo, use_container_width=True)