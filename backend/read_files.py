import pandas as pd
import os
import glob
import re

# Caminho base onde estão os .txt
BASE_DIR = r"C:\Users\U33V\OneDrive - PETROBRAS\Desktop\Auto_CL\Fase 2 - Arquivos de Excel Reduzidos\TEMP"

# Caminho para salvar o JSON (um nível acima da pasta backend)
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CAMINHO_JSON = os.path.join(DASHBOARD_DIR, "requests.json")

# Colunas de interesse
coluna_chave = "Def.projeto"
colunas_valores = [
    "Valor/Moeda obj",
    "Valor total em reais",
    "Val suj cont loc R$",
    "Valor cont local R$",
    "Valor/moeda ACC"
]

dfs = []

# Procura todos os .txt no diretório
for arquivo in glob.glob(os.path.join(BASE_DIR, "*.txt")):
    try:
        # Detecta delimitador automaticamente
        with open(arquivo, 'r', encoding='utf-8') as f:
            primeira_linha = f.readline()
        sep = ';' if ';' in primeira_linha else '\t'

        df = pd.read_csv(arquivo, sep=sep, encoding='utf-8', dtype=str)
        print(f" Lido: {os.path.basename(arquivo)} ({len(df)} linhas)")

        # Garante que a coluna-chave e colunas numéricas existam
        colunas_existentes = [c for c in colunas_valores if c in df.columns]
        if coluna_chave not in df.columns:
            print(f"⚠️ Coluna '{coluna_chave}' não encontrada em {arquivo}")
            continue

        # Função de limpeza de valores
        def limpar_valor(v):
            if pd.isna(v):
                return 0.0
            v = str(v).strip()
            v = v.replace("R$", "").replace(" ", "")
            v = v.replace(",", ".")
            v = re.sub(r"[^0-9.\-]", "", v)
            if v.count('.') > 1:
                partes = v.split('.')
                v = ''.join(partes[:-1]) + '.' + partes[-1]
            try:
                return float(v)
            except:
                return 0.0

        # Aplica a limpeza nas colunas numéricas
        for c in colunas_existentes:
            df[c] = df[c].apply(limpar_valor)

        dfs.append(df[[coluna_chave] + colunas_existentes])

    except Exception as e:
        print(f" Erro ao processar {arquivo}: {e}")

# Junta e processa tudo
if not dfs:
    print(" Nenhum arquivo processado.")
else:
    df_total = pd.concat(dfs, ignore_index=True)

    # Agrupa e soma
    resultado = df_total.groupby(coluna_chave, as_index=False)[colunas_valores].sum()

    # Exporta para JSON
    resultado.to_json(CAMINHO_JSON, orient="records", force_ascii=False, indent=2)

    print(f"\n JSON salvo em: {CAMINHO_JSON}")
