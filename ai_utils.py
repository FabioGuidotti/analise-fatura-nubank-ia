from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extrair_transacoes_com_ai(texto, categorias):
    categorias_str = ", ".join(categorias)
    prompt = f"""
    Extraia as transações financeiras do seguinte texto de uma fatura de cartão de crédito.
    Entre as transações existe uma linha que se refere ao valor pago na fatura, sua descriação inicia com "Pagamento em...", esse valor não deve ser considerado nas transações.
    Retorne apenas uma lista de dicionários Python, onde cada dicionário representa uma transação com as chaves 'data', 'descricao', 'valor' e 'categoria'.
    Use o formato de data YYYY-MM-DD.
    Para a categoria, escolha uma das seguintes opções: {categorias_str}. Se nenhuma categoria se aplicar, use 'Outros'.
    Não inclua nenhum texto adicional na sua resposta, apenas a lista de dicionários.

    Texto da fatura:
    {texto}

    Formato da resposta:
    [
        {{"data": "YYYY-MM-DD", "descricao": "Descrição da transação", "valor": "XXX,XX", "categoria": "Categoria"}},
        ...
    ]
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em extrair e categorizar informações de faturas de cartão de crédito."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    try:
        transacoes = eval(response.choices[0].message.content)
        return transacoes
    except:
        st.error("Erro ao processar a resposta da IA. Verifique o formato da fatura.")
        return None

def conversar_com_ai(pergunta, dados_fatura):
    transacoes_str = dados_fatura.to_string(index=False)
    contexto = f"""
    Você é um assistente financeiro especializado em análise de faturas de cartão de crédito.
    Você tem acesso aos seguintes dados da fatura:

    Resumo:
    - Total gasto: R$ {dados_fatura['Valor'].sum():.2f}
    - Média de gastos: R$ {dados_fatura['Valor'].mean():.2f}
    - Maior gasto: R$ {dados_fatura['Valor'].max():.2f}
    - Menor gasto: R$ {dados_fatura['Valor'].min():.2f}
    - Número de transações: {len(dados_fatura)}
    - Período da fatura: de {dados_fatura['Data'].min().strftime('%d/%m/%Y')} a {dados_fatura['Data'].max().strftime('%d/%m/%Y')}
    - Categorias de gastos: {', '.join(dados_fatura['Categoria'].unique())}

    Dados completos das transações:
    {transacoes_str}

    Analise esses dados e responda à pergunta do usuário com base nessas informações e em seu conhecimento geral sobre finanças pessoais.
    Forneça insights detalhados e, quando apropriado, sugira maneiras de melhorar os hábitos financeiros.
    """

    prompt = f"{contexto}\n\nPergunta do usuário: {pergunta}\n\nResposta:"

    return client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro especializado em análise de faturas de cartão de crédito."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
        stream=True
    )