import argparse
from datetime import datetime
import logging
import hashlib
import ollama

logging.basicConfig(
    filename='integridade.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def gerar_hash(caminho):
    try:
        with open(caminho, "rb") as arq_bin:
            conteudo = arq_bin.read()
            return hashlib.sha256(conteudo).hexdigest()
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {caminho}")
        return None

def analisar_risco_com_ia(hash1, hash2):
    """
    Chama o modelo Ollama local em streaming, apenas explicando
    o que fazer após detectar diferença de hashes. Resposta objetiva,
    no máximo 150 palavras, aparecendo em tempo real.
    """
    try:
        stream = ollama.chat(
            model='phi3',  # modelo leve, pode trocar para 'llama3' se quiser
            messages=[
                {
                    "role": "system",
                    "content": "Você é um analista de segurança direto e objetivo."
                },
                {
                    "role": "user",
                    "content": f"""
                    Dois arquivos tiveram hashes diferentes.

                    Hash original: {hash1}
                    Hash novo: {hash2}

                    Explique APENAS o que deve ser feito depois dessa diferença.
                    - Máximo 150 palavras
                    - Use o mínimo de palavras possível
                    - Seja direto
                    """
                }
            ],
            stream=True,
            options={
                "num_predict": 200  # limita tokens para não gerar respostas longas
            }
        )

        print()  # quebra de linha antes da resposta
        # imprimir em tempo real
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print("\n")

    except Exception as e:
        print(f"Erro ao consultar modelo local: {e}")

def main():
    parser = argparse.ArgumentParser(description="CALCULADORA DE INTEGRIDADE DE ARQUIVOS")
    parser.add_argument("--original", help="CAMINHO DO ARQUIVO ORIGINAL")
    parser.add_argument("--novo", help="CAMINHO DO ARQUIVO NOVO PARA COMPARAR")
    argumento = parser.parse_args()

    if not argumento.original:
        argumento.original = input("Digite o caminho do ARQUIVO ORIGINAL: ")
    if not argumento.novo:
        argumento.novo = input("Digite o caminho do ARQUIVO NOVO: ")

    logging.info("Iniciando verificação de integridade")

    print("\n----- VERIFICAÇÃO DE INTEGRIDADE -----")
    print(f"Data: {datetime.now().strftime('%d/%m/%Y')} | Hora: {datetime.now().strftime('%H:%M:%S')}")

    hash1 = gerar_hash(argumento.original)
    hash2 = gerar_hash(argumento.novo)

    if not hash1 or not hash2:
        print("FALHA NA LEITURA: Um dos arquivos não foi encontrado. Verifique o log.")
        return

    print(f"\nHash do arquivo ORIGINAL: {hash1}")
    print(f"Hash do arquivo NOVO:     {hash2}")

    if hash1 == hash2:
        print("\nNenhuma alteração detectada. Os arquivos são idênticos!")
        logging.info("Arquivos idênticos.")
    else:
        print("\nALERTA: Alteração detectada. Os arquivos são diferentes!")
        logging.warning("Hashes diferentes — possível modificação.")

        print("\n--- Análise de Risco com IA (Ollama Local) ---")
        analisar_risco_com_ia(hash1, hash2)

if __name__ == "__main__":
    main()