import streamlit as st
from data_processing import importar_fatura_nubank_pdf
from database import salvar_dados

def tela_importar_fatura():
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Por favor, faça login para acessar esta página.")
        return

    usuario_id = st.session_state.user.id

    st.subheader("Importação da Fatura")
    faturas = st.file_uploader("Importar fatura(s) do cartão Nubank (PDF)", type=["pdf"], accept_multiple_files=True)
    if faturas:
        for fatura in faturas:
            st.write(f"Processando fatura: {fatura.name}")
            novos_dados_fatura = importar_fatura_nubank_pdf(fatura, usuario_id)
            if novos_dados_fatura is not None:
                st.write(f"Dados extraídos da fatura {fatura.name}:")
                st.write(novos_dados_fatura)
                
                if isinstance(novos_dados_fatura, dict):
                    novos_dados_fatura = [novos_dados_fatura]
                elif isinstance(novos_dados_fatura, list) and all(isinstance(item, str) for item in novos_dados_fatura):
                    novos_dados_fatura = [{
                        'data': novos_dados_fatura[0],
                        'descricao': novos_dados_fatura[1],
                        'valor': novos_dados_fatura[2],
                        'categoria': novos_dados_fatura[3] if len(novos_dados_fatura) > 3 else 'Não categorizado'
                    }]
                
                st.write("Dados formatados para salvar:")
                st.write(novos_dados_fatura)
                
                try:
                    salvar_dados(novos_dados_fatura, fatura.name, usuario_id)
                    st.success(f"Fatura {fatura.name} importada e salva com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar dados da fatura {fatura.name}: {str(e)}")
                    st.write("Detalhes do erro:", e)
            else:
                st.error(f"Falha ao importar a fatura {fatura.name}. Verifique o formato do arquivo ou o conteúdo da fatura.")
        st.success("Todas as faturas foram processadas!")