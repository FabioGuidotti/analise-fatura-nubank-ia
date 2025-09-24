import streamlit as st
import pandas as pd
from database import carregar_dados
from ai_utils import conversar_com_ai

def tela_conversar_ia():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id
    
    dados_fatura = carregar_dados(usuario_id)
    if not dados_fatura.empty:
        st.subheader("🤖 Conversa com IA")
        st.write("Faça perguntas sobre sua fatura e obtenha insights da IA.")
        
        # Seção de Filtros
        with st.expander("🔍 Filtros para Análise", expanded=False):
            # Converter coluna de data se necessário
            if 'Data' in dados_fatura.columns:
                dados_fatura['Data'] = pd.to_datetime(dados_fatura['Data'])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Filtro por período
                data_min = dados_fatura['Data'].min().date()
                data_max = dados_fatura['Data'].max().date()
                
                periodo = st.date_input(
                    "Período",
                    value=(data_min, data_max),
                    min_value=data_min,
                    max_value=data_max,
                    help="Selecione o período para análise"
                )
            
            with col2:
                # Filtro por categoria
                categorias = ['Todas'] + sorted(dados_fatura['Categoria'].unique().tolist())
                categoria_selecionada = st.selectbox(
                    "Categoria",
                    categorias,
                    help="Filtrar por categoria específica"
                )
            
            with col3:
                # Filtro por valor mínimo
                valor_min = st.number_input(
                    "Valor Mínimo (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    help="Mostrar apenas gastos acima deste valor"
                )
            
            with col4:
                # Filtro por arquivo de origem
                arquivos = ['Todos'] + sorted(dados_fatura['Arquivo de Origem'].unique().tolist())
                arquivo_selecionado = st.selectbox(
                    "Arquivo",
                    arquivos,
                    help="Filtrar por arquivo de origem"
                )
            
            # Aplicar filtros
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
            
            # Mostrar resumo dos filtros aplicados
            st.info(f"📊 Analisando {len(dados_filtrados)} transações de {len(dados_fatura)} total")
        
        # Usar dados filtrados se os filtros foram aplicados, senão usar dados originais
        if 'dados_filtrados' in locals() and not dados_filtrados.empty:
            dados_para_analise = dados_filtrados
        else:
            dados_para_analise = dados_fatura
        
        # Inicializar mensagens se não existir
        if "mensagens" not in st.session_state:
            st.session_state.mensagens = []

        # Mostrar histórico de conversa
        for mensagem in st.session_state.mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])

        # Verificar se há uma nova pergunta para processar
        if st.session_state.mensagens and len(st.session_state.mensagens) > 0:
            ultima_mensagem = st.session_state.mensagens[-1]
            if ultima_mensagem["role"] == "user":
                # Verificar se já foi processada (se não há resposta correspondente)
                if len(st.session_state.mensagens) == 1 or st.session_state.mensagens[-2]["role"] != "assistant":
                    pergunta = ultima_mensagem["content"]
                    
                    # Mostrar pergunta do usuário
                    with st.chat_message("user"):
                        st.markdown(pergunta)

                    # Processar resposta da IA
                    with st.chat_message("assistant"):
                        resposta_placeholder = st.empty()
                        resposta_completa = ""
                        
                        try:
                            response = conversar_com_ai(pergunta, dados_para_analise)
                            
                            # Verificar se é streaming ou não
                            if hasattr(response, '__iter__') and not isinstance(response, str):
                                # Streaming response
                                for chunk in response:
                                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                                        if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content is not None:
                                            resposta_completa += chunk.choices[0].delta.content
                                            resposta_placeholder.markdown(resposta_completa + "▌")
                            else:
                                # Non-streaming response
                                if hasattr(response, 'choices') and len(response.choices) > 0:
                                    resposta_completa = response.choices[0].message.content
                                else:
                                    resposta_completa = str(response)
                            
                            resposta_placeholder.markdown(resposta_completa)
                            
                        except Exception as e:
                            st.error(f"Erro ao processar pergunta: {str(e)}")
                            print(f"Erro detalhado: {e}")
                            import traceback
                            traceback.print_exc()
                            resposta_completa = "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente."

                        # Adicionar resposta ao histórico
                        st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})

        # Input para pergunta manual
        pergunta = st.chat_input("Faça uma pergunta sobre sua fatura:")

        if pergunta:
            # Adicionar pergunta ao histórico
            st.session_state.mensagens.append({"role": "user", "content": pergunta})
            st.rerun()

        # Botões de controle (mais compactos)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Limpar", help="Limpar histórico da conversa"):
                st.session_state.mensagens = []
                st.success("Histórico limpo!")
                st.rerun()
        
        with col2:
            if st.button("📊 Resumo", help="Pedir resumo dos gastos"):
                pergunta = "Me dê um resumo geral dos meus gastos"
                st.session_state.mensagens.append({"role": "user", "content": pergunta})
                st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                st.rerun()
        
        with col3:
            if st.button("💰 Análise", help="Análise detalhada dos gastos"):
                pergunta = "Faça uma análise detalhada dos meus gastos"
                st.session_state.mensagens.append({"role": "user", "content": pergunta})
                st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                st.rerun()
        
        with col4:
            if st.button("💡 Dicas", help="Sugestões de economia"):
                pergunta = "Quais dicas você tem para melhorar meus hábitos financeiros?"
                st.session_state.mensagens.append({"role": "user", "content": pergunta})
                st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                st.rerun()
        
        # Sugestões de perguntas (mais compactas)
        with st.expander("💡 Sugestões de Perguntas", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Resumo Geral", key="sugestao1"):
                    pergunta = "Me dê um resumo geral dos meus gastos"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
                
                if st.button("💰 Maiores Gastos", key="sugestao2"):
                    pergunta = "Quais são meus maiores gastos?"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
                
                if st.button("📈 Por Categoria", key="sugestao3"):
                    pergunta = "Como estão meus gastos por categoria?"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
            
            with col2:
                if st.button("🎯 Economia", key="sugestao4"):
                    pergunta = "Posso economizar em algo?"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
                
                if st.button("📅 Padrões", key="sugestao5"):
                    pergunta = "Quais padrões você identifica nos meus gastos?"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
                
                if st.button("💡 Dicas", key="sugestao6"):
                    pergunta = "Quais dicas você tem para melhorar meus hábitos financeiros?"
                    st.session_state.mensagens.append({"role": "user", "content": pergunta})
                    st.success("✅ Pergunta adicionada! A resposta aparecerá abaixo.")
                    st.rerun()
    else:
        st.warning("Nenhuma fatura importada ainda. Por favor, importe uma fatura primeiro.")