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
    # Remove símbolos de moeda e espaços, depois converte separadores decimais
    df['valor'] = df['valor'].str.replace('R$', '').str.replace('$', '').str.strip()
    
    # Função para converter valor de forma segura
    def converter_valor(valor_str):
        try:
            import re
            
            # Remove símbolos de moeda e espaços
            valor_limpo = str(valor_str).replace('R$', '').replace('$', '').strip()
            
            # Se contém vírgula, assume formato brasileiro (1.250,50)
            if ',' in valor_limpo:
                # Remove pontos de milhares e converte vírgula para ponto decimal
                valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
            # Se contém apenas pontos, verifica se é formato americano (15.75)
            elif '.' in valor_limpo:
                # Conta quantos pontos existem
                pontos = valor_limpo.count('.')
                if pontos == 1:
                    # Apenas um ponto, provavelmente decimal
                    pass  # Mantém como está
                else:
                    # Múltiplos pontos, provavelmente separadores de milhares
                    # Remove todos os pontos exceto o último
                    partes = valor_limpo.split('.')
                    if len(partes) > 2:
                        valor_limpo = ''.join(partes[:-1]) + '.' + partes[-1]
            
            return float(valor_limpo)
        except (ValueError, AttributeError):
            # Se falhar, tenta extrair apenas números
            import re
            numeros = re.findall(r'[\d,]+', str(valor_str))
            if numeros:
                return float(numeros[0].replace(',', '.'))
            return 0.0
    
    df['valor'] = df['valor'].apply(converter_valor)
    
    # Renomear e reordenar as colunas
    df = df.rename(columns={'descricao': 'descricao', 'categoria': 'categoria'})
    df = df[['data', 'descricao', 'valor', 'categoria']]

    return df if not df.empty else None