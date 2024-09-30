import pandas as pd
import pdfplumber
from ai_utils import extrair_transacoes_com_ai
from database import obter_categorias

def importar_fatura_nubank_pdf(arquivo, usuario_id):
    # Extrair texto do PDF
    with pdfplumber.open(arquivo) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()

    # Obter categorias do banco de dados
    categorias = obter_categorias(usuario_id)

    # Usar IA para extrair as transações
    transacoes = extrair_transacoes_com_ai(texto_completo, categorias)

    if transacoes is None:
        return None

    # Converter as informações para um DataFrame
    df = pd.DataFrame(transacoes)
    
    # Converter a coluna 'data' para datetime
    df['data'] = pd.to_datetime(df['data'])
    
    # Converter a coluna 'valor' para float
    df['valor'] = df['valor'].str.replace('.', '').str.replace(',', '.').astype(float)
    
    # Renomear e reordenar as colunas
    df = df.rename(columns={'descricao': 'descricao', 'categoria': 'categoria'})
    df = df[['data', 'descricao', 'valor', 'categoria']]

    return df if not df.empty else None