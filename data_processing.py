import pandas as pd
import pdfplumber
from ai_utils import extrair_transacoes_com_ai
from database import obter_categorias_com_exemplos_para_ia

def importar_fatura_nubank_pdf(arquivo, usuario_id):
    try:
        # Extrair texto do PDF
        with pdfplumber.open(arquivo) as pdf:
            texto_completo = ""
            total_paginas = len(pdf.pages)
            print(f"PDF possui {total_paginas} páginas")
            
            for i, pagina in enumerate(pdf.pages):
                print(f"Processando página {i+1}/{total_paginas}")
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
                    print(f"Página {i+1}: {len(texto_pagina)} caracteres extraídos")
                else:
                    print(f"Página {i+1}: Nenhum texto extraído")
        
        if not texto_completo.strip():
            print("Erro: Nenhum texto foi extraído do PDF")
            return None
        
        print(f"Texto total extraído: {len(texto_completo)} caracteres")
        print(f"Primeiros 500 caracteres: {texto_completo[:500]}...")
        print(f"Últimos 500 caracteres: {texto_completo[-500:]}...")

        # Obter categorias com exemplos do banco de dados
        categorias_com_exemplos = obter_categorias_com_exemplos_para_ia(usuario_id)
        print(f"Categorias disponíveis: {len(categorias_com_exemplos)} categorias")

        # Verificar se o texto é muito grande e dividir se necessário
        MAX_CHARS = 15000  # Limite de caracteres por chunk
        if len(texto_completo) > MAX_CHARS:
            print(f"Texto muito grande ({len(texto_completo)} chars), dividindo em chunks...")
            chunks = dividir_texto_em_chunks(texto_completo, MAX_CHARS)
            print(f"Texto dividido em {len(chunks)} chunks")
            
            todas_transacoes = []
            for i, chunk in enumerate(chunks):
                print(f"Processando chunk {i+1}/{len(chunks)} ({len(chunk)} caracteres)")
                transacoes_chunk = extrair_transacoes_com_ai(chunk, categorias_com_exemplos)
                if transacoes_chunk:
                    todas_transacoes.extend(transacoes_chunk)
                    print(f"Chunk {i+1}: {len(transacoes_chunk)} transações extraídas")
                else:
                    print(f"Chunk {i+1}: Nenhuma transação extraída")
            
            transacoes = todas_transacoes
        else:
            # Usar IA para extrair as transações
            transacoes = extrair_transacoes_com_ai(texto_completo, categorias_com_exemplos)

        if transacoes is None:
            print("Erro: A IA não conseguiu extrair transações")
            return None
        
        if len(transacoes) == 0:
            print("Aviso: Nenhuma transação foi encontrada")
            return None
            
        print(f"Total de transações extraídas: {len(transacoes)}")
        
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
        
    except Exception as e:
        print(f"Erro ao processar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def dividir_texto_em_chunks(texto, tamanho_maximo):
    """Divide o texto em chunks menores, tentando manter a integridade das linhas"""
    chunks = []
    linhas = texto.split('\n')
    chunk_atual = ""
    
    for linha in linhas:
        # Se adicionar esta linha exceder o tamanho máximo, salvar chunk atual e começar novo
        if len(chunk_atual) + len(linha) + 1 > tamanho_maximo and chunk_atual:
            chunks.append(chunk_atual.strip())
            chunk_atual = linha
        else:
            chunk_atual += linha + '\n'
    
    # Adicionar o último chunk se não estiver vazio
    if chunk_atual.strip():
        chunks.append(chunk_atual.strip())
    
    return chunks