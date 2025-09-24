import os
import json
import ast
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o cliente OpenAI com a chave API do arquivo .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extrair_transacoes_com_ai(texto, categorias_com_exemplos):
    # Garantir que sempre temos a categoria "Outros" disponível
    if not any("Outros" in cat for cat in categorias_com_exemplos):
        categorias_com_exemplos.append("- Outros")
    
    categorias_str = "\n".join(categorias_com_exemplos)
    prompt = f"""
    Você é um especialista em extrair transações de faturas de cartão de crédito.

    TAREFA: Extrair TODAS as transações financeiras do texto abaixo.
    
    REGRAS IMPORTANTES:
    1. IGNORE linhas que começam com "Pagamento em" ou "PAGAMENTO"
    2. IGNORE totais, resumos e cabeçalhos
    3. Extraia APENAS transações individuais de compras/gastos
    4. Retorne EXATAMENTE no formato JSON abaixo, sem texto adicional
    
    FORMATO OBRIGATÓRIO:
    [
        {{"data": "YYYY-MM-DD", "descricao": "NOME DO ESTABELECIMENTO", "valor": "XXX,XX", "categoria": "CATEGORIA"}},
        {{"data": "YYYY-MM-DD", "descricao": "NOME DO ESTABELECIMENTO", "valor": "XXX,XX", "categoria": "CATEGORIA"}}
    ]
    
    CATEGORIAS DISPONÍVEIS:
    {categorias_str}
    
    Use os exemplos fornecidos para classificar corretamente cada transação.
    
    TEXTO DA FATURA:
    {texto}
    
    RESPOSTA (apenas JSON):
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em extrair e categorizar informações de faturas de cartão de crédito."},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        resposta_ia = response.choices[0].message.content.strip()
        
        # Log completo da resposta para debug
        print(f"=== RESPOSTA COMPLETA DA IA ===")
        print(resposta_ia)
        print(f"=== FIM DA RESPOSTA ===")
        
        # Tentar diferentes métodos de parsing
        transacoes = None
        
        # Método 1: Tentar usar ast.literal_eval (mais seguro que eval)
        try:
            print("Tentando ast.literal_eval...")
            transacoes = ast.literal_eval(resposta_ia)
            print("✅ Sucesso com ast.literal_eval")
        except (ValueError, SyntaxError) as e:
            print(f"❌ Erro no ast.literal_eval: {e}")
            
            # Método 2: Tentar extrair JSON da resposta
            try:
                print("Tentando parsing JSON...")
                import re
                
                # Primeiro, tentar remover markdown se presente
                resposta_limpa = resposta_ia
                if '```json' in resposta_ia:
                    print("Removendo markdown ```json...")
                    json_match = re.search(r'```json\s*(.*?)\s*```', resposta_ia, re.DOTALL)
                    if json_match:
                        resposta_limpa = json_match.group(1).strip()
                        print(f"JSON extraído: {resposta_limpa[:100]}...")
                elif '```' in resposta_ia:
                    print("Removendo markdown ```...")
                    json_match = re.search(r'```\s*(.*?)\s*```', resposta_ia, re.DOTALL)
                    if json_match:
                        resposta_limpa = json_match.group(1).strip()
                        print(f"JSON extraído: {resposta_limpa[:100]}...")
                
                # Procurar por padrões de lista JSON na resposta limpa
                json_match = re.search(r'\[.*\]', resposta_limpa, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    print(f"Lista JSON encontrada: {json_str[:100]}...")
                    transacoes = json.loads(json_str)
                    print("✅ Sucesso com JSON parsing")
                else:
                    print("Tentando usar resposta limpa diretamente...")
                    transacoes = json.loads(resposta_limpa)
                    print("✅ Sucesso com resposta limpa")
            except Exception as e2:
                print(f"❌ Erro no parsing JSON: {e2}")
                
                # Método 3: Tentar usar eval como último recurso
                try:
                    print("Tentando eval como último recurso...")
                    transacoes = eval(resposta_ia)
                    print("✅ Sucesso com eval")
                except Exception as e3:
                    print(f"❌ Erro no eval: {e3}")
                    
                    # Método 4: Tentar extrair manualmente usando regex
                    try:
                        print("Tentando extração manual...")
                        transacoes = extrair_transacoes_manual(resposta_ia)
                        if transacoes:
                            print(f"✅ Sucesso com extração manual: {len(transacoes)} transações")
                        else:
                            print("❌ Extração manual não retornou transações")
                    except Exception as e4:
                        print(f"❌ Erro na extração manual: {e4}")
                        raise e4
        
        # Validar se as transações foram extraídas corretamente
        if not isinstance(transacoes, list):
            raise ValueError("A resposta não é uma lista de transações")
        
        if len(transacoes) == 0:
            st.warning("Nenhuma transação foi encontrada na fatura.")
            return []
        
        # Validar estrutura das transações
        for i, transacao in enumerate(transacoes):
            if not isinstance(transacao, dict):
                raise ValueError(f"Transação {i} não é um dicionário")
            
            campos_obrigatorios = ['data', 'descricao', 'valor', 'categoria']
            for campo in campos_obrigatorios:
                if campo not in transacao:
                    raise ValueError(f"Transação {i} não possui o campo '{campo}'")
        
        print(f"Sucesso: {len(transacoes)} transações extraídas")
        return transacoes
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        print(f"Resposta da IA que causou erro: {response.choices[0].message.content}")
        
        # Tentar extração de emergência
        try:
            print("🆘 Tentando extração de emergência...")
            transacoes_emergencia = extrair_transacoes_emergencia(response.choices[0].message.content)
            if transacoes_emergencia:
                print(f"✅ Extração de emergência bem-sucedida: {len(transacoes_emergencia)} transações")
                return transacoes_emergencia
        except Exception as e2:
            print(f"❌ Extração de emergência também falhou: {e2}")
        
        st.error(f"Erro ao processar a resposta da IA: {str(e)}")
        st.error("Resposta da IA recebida:")
        st.code(response.choices[0].message.content[:500] + "..." if len(response.choices[0].message.content) > 500 else response.choices[0].message.content)
        return None

def extrair_transacoes_emergencia(texto_resposta):
    """Extração de emergência usando métodos mais agressivos"""
    import re
    
    print("🚨 Iniciando extração de emergência...")
    transacoes = []
    
    # Método 1: Procurar por qualquer padrão que pareça uma transação
    padroes = [
        r'\{[^}]*"data"[^}]*"descricao"[^}]*"valor"[^}]*"categoria"[^}]*\}',
        r'\{[^}]*"data"[^}]*"descricao"[^}]*"valor"[^}]*\}',
        r'\{[^}]*"data"[^}]*"descricao"[^}]*\}',
        r'\{[^}]*"data"[^}]*\}',
    ]
    
    for i, padrao in enumerate(padroes):
        print(f"Tentando padrão {i+1}: {padrao}")
        matches = re.findall(padrao, texto_resposta, re.DOTALL)
        print(f"Encontrados {len(matches)} matches")
        
        for j, match in enumerate(matches):
            try:
                # Limpar o match
                match_limpo = match.replace("'", '"').replace('\n', ' ').replace('\r', ' ')
                
                # Tentar diferentes métodos de parsing
                transacao = None
                
                # Método A: JSON direto
                try:
                    transacao = json.loads(match_limpo)
                except:
                    pass
                
                # Método B: Eval
                if not transacao:
                    try:
                        transacao = eval(match_limpo)
                    except:
                        pass
                
                # Método C: Regex para extrair campos
                if not transacao:
                    try:
                        data_match = re.search(r'"data"\s*:\s*"([^"]*)"', match_limpo)
                        desc_match = re.search(r'"descricao"\s*:\s*"([^"]*)"', match_limpo)
                        valor_match = re.search(r'"valor"\s*:\s*"([^"]*)"', match_limpo)
                        cat_match = re.search(r'"categoria"\s*:\s*"([^"]*)"', match_limpo)
                        
                        if data_match and desc_match and valor_match:
                            transacao = {
                                'data': data_match.group(1),
                                'descricao': desc_match.group(1),
                                'valor': valor_match.group(1),
                                'categoria': cat_match.group(1) if cat_match else 'Outros'
                            }
                    except:
                        pass
                
                if transacao and isinstance(transacao, dict):
                    # Validar campos obrigatórios
                    if 'data' in transacao and 'descricao' in transacao and 'valor' in transacao:
                        if 'categoria' not in transacao:
                            transacao['categoria'] = 'Outros'
                        transacoes.append(transacao)
                        print(f"✅ Transação {j+1} extraída com sucesso")
                    else:
                        print(f"⚠️ Transação {j+1} não tem campos obrigatórios")
                else:
                    print(f"❌ Transação {j+1} não pôde ser parseada")
                    
            except Exception as e:
                print(f"❌ Erro ao processar match {j+1}: {e}")
                continue
        
        if transacoes:
            print(f"✅ Padrão {i+1} funcionou: {len(transacoes)} transações")
            break
    
    # Método 2: Extração linha por linha mais agressiva
    if not transacoes:
        print("Tentando extração linha por linha agressiva...")
        linhas = texto_resposta.split('\n')
        for i, linha in enumerate(linhas):
            if '{' in linha and '}' in linha:
                try:
                    # Extrair tudo entre { e }
                    inicio = linha.find('{')
                    fim = linha.rfind('}') + 1
                    json_str = linha[inicio:fim]
                    
                    if json_str:
                        # Tentar diferentes limpezas
                        for limpeza in [
                            lambda x: x.replace("'", '"'),
                            lambda x: x.replace("'", '"').replace('\n', ' '),
                            lambda x: x.replace("'", '"').replace('\n', ' ').replace('\r', ' '),
                        ]:
                            try:
                                json_limpo = limpeza(json_str)
                                transacao = json.loads(json_limpo)
                                
                                if isinstance(transacao, dict) and 'data' in transacao and 'descricao' in transacao and 'valor' in transacao:
                                    if 'categoria' not in transacao:
                                        transacao['categoria'] = 'Outros'
                                    transacoes.append(transacao)
                                    print(f"✅ Linha {i+1} processada com sucesso")
                                    break
                            except:
                                continue
                except:
                    continue
    
    print(f"🚨 Extração de emergência concluída: {len(transacoes)} transações")
    return transacoes

def extrair_transacoes_manual(texto_resposta):
    """Extrai transações manualmente usando regex quando o parsing automático falha"""
    import re
    
    print("Iniciando extração manual...")
    print(f"Texto para extrair: {texto_resposta[:200]}...")
    
    transacoes = []
    
    # Método 1: Procurar por dicionários completos
    padrao_completo = r'\{[^}]*"data"[^}]*"descricao"[^}]*"valor"[^}]*"categoria"[^}]*\}'
    matches = re.findall(padrao_completo, texto_resposta, re.DOTALL)
    print(f"Encontrados {len(matches)} matches com padrão completo")
    
    for i, match in enumerate(matches):
        try:
            print(f"Processando match {i+1}: {match[:50]}...")
            # Limpar e formatar o match
            match_limpo = match.replace("'", '"')  # Converter aspas simples para duplas
            transacao = json.loads(match_limpo)
            transacoes.append(transacao)
            print(f"✅ Match {i+1} processado com sucesso")
        except Exception as e:
            print(f"❌ Erro no match {i+1}: {e}")
            continue
    
    # Método 2: Se não encontrou nada, tentar padrão mais flexível
    if not transacoes:
        print("Tentando padrão mais flexível...")
        padrao_flexivel = r'\{[^}]*"data"[^}]*\}'
        matches_flex = re.findall(padrao_flexivel, texto_resposta, re.DOTALL)
        print(f"Encontrados {len(matches_flex)} matches com padrão flexível")
        
        for i, match in enumerate(matches_flex):
            try:
                print(f"Processando match flexível {i+1}: {match[:50]}...")
                match_limpo = match.replace("'", '"')
                transacao = json.loads(match_limpo)
                
                # Verificar se tem os campos obrigatórios
                campos_obrigatorios = ['data', 'descricao', 'valor', 'categoria']
                if all(campo in transacao for campo in campos_obrigatorios):
                    transacoes.append(transacao)
                    print(f"✅ Match flexível {i+1} processado com sucesso")
                else:
                    print(f"⚠️ Match flexível {i+1} não tem todos os campos obrigatórios")
            except Exception as e:
                print(f"❌ Erro no match flexível {i+1}: {e}")
                continue
    
    # Método 3: Extrair linha por linha se ainda não encontrou nada
    if not transacoes:
        print("Tentando extração linha por linha...")
        linhas = texto_resposta.split('\n')
        for i, linha in enumerate(linhas):
            if '{' in linha and '}' in linha:
                try:
                    # Extrair JSON da linha
                    inicio = linha.find('{')
                    fim = linha.rfind('}') + 1
                    json_str = linha[inicio:fim]
                    
                    if json_str:
                        json_str = json_str.replace("'", '"')
                        transacao = json.loads(json_str)
                        
                        campos_obrigatorios = ['data', 'descricao', 'valor', 'categoria']
                        if all(campo in transacao for campo in campos_obrigatorios):
                            transacoes.append(transacao)
                            print(f"✅ Linha {i+1} processada com sucesso")
                except Exception as e:
                    continue
    
    print(f"Extração manual concluída: {len(transacoes)} transações encontradas")
    return transacoes

def testar_extracao_ia(texto_exemplo, categorias_com_exemplos):
    """Função de teste para verificar se a extração de transações está funcionando"""
    try:
        print("=== TESTE DE EXTRAÇÃO DE TRANSAÇÕES ===")
        print(f"Texto de exemplo: {texto_exemplo[:100]}...")
        print(f"Categorias: {categorias_com_exemplos}")
        
        resultado = extrair_transacoes_com_ai(texto_exemplo, categorias_com_exemplos)
        
        if resultado:
            print(f"✅ Sucesso: {len(resultado)} transações extraídas")
            for i, transacao in enumerate(resultado):
                print(f"  {i+1}. {transacao}")
        else:
            print("❌ Falha: Nenhuma transação extraída")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return None

def conversar_com_ai(pergunta, dados_fatura):
    import pandas as pd
    
    # Converter coluna de data se necessário
    dados_fatura_copy = dados_fatura.copy()
    if 'Data' in dados_fatura_copy.columns:
        dados_fatura_copy['Data'] = pd.to_datetime(dados_fatura_copy['Data'])
    
    transacoes_str = dados_fatura_copy.to_string(index=False)
    
    # Calcular período de forma segura
    try:
        data_min = dados_fatura_copy['Data'].min().strftime('%d/%m/%Y')
        data_max = dados_fatura_copy['Data'].max().strftime('%d/%m/%Y')
        periodo_str = f"de {data_min} a {data_max}"
    except:
        periodo_str = "período não disponível"
    
    contexto = f"""
    Você é um assistente financeiro especializado em análise de faturas de cartão de crédito.
    Você tem acesso aos seguintes dados da fatura:

    Resumo:
    - Total gasto: R$ {dados_fatura_copy['Valor'].sum():.2f}
    - Média de gastos: R$ {dados_fatura_copy['Valor'].mean():.2f}
    - Maior gasto: R$ {dados_fatura_copy['Valor'].max():.2f}
    - Menor gasto: R$ {dados_fatura_copy['Valor'].min():.2f}
    - Número de transações: {len(dados_fatura_copy)}
    - Período da fatura: {periodo_str}
    - Categorias de gastos: {', '.join(dados_fatura_copy['Categoria'].unique())}

    Dados completos das transações:
    {transacoes_str}

    Analise esses dados e responda à pergunta do usuário com base nessas informações e em seu conhecimento geral sobre finanças pessoais.
    Forneça insights detalhados e, quando apropriado, sugira maneiras de melhorar os hábitos financeiros.
    """

    prompt = f"{contexto}\n\nPergunta do usuário: {pergunta}\n\nResposta:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente financeiro especializado em análise de faturas de cartão de crédito."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000,
            stream=True
        )
        return response
    except Exception as e:
        print(f"Erro na API: {e}")
        # Fallback para modelo sem streaming
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente financeiro especializado em análise de faturas de cartão de crédito."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
            )
            return response
        except Exception as e2:
            print(f"Erro no fallback: {e2}")
            raise e2