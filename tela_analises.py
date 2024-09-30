import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
            gastos_por_categoria = gastos_por_categoria.append({coluna_categoria: "Outros", coluna_valor: 0}, ignore_index=True)
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

    st.subheader("Análises da Fatura")
    dados_fatura = carregar_dados(usuario_id)
    if not dados_fatura.empty:
        criar_graficos_analise(dados_fatura)
        
        st.subheader("Resumo Estatístico")
        st.write(dados_fatura['Valor'].describe())
        
        st.subheader("Maiores Gastos")
        maiores_gastos = dados_fatura.nlargest(5, 'Valor')
        st.table(maiores_gastos[['Data', 'Descrição', 'Valor', 'Categoria']])
        
        st.subheader("Gastos por Categoria")
        gastos_por_categoria = dados_fatura.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        st.bar_chart(gastos_por_categoria)
    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")

    datas_faturas = obter_datas_faturas(usuario_id)
    arquivos_origem = obter_arquivos_origem(usuario_id)