import pandas as pd
import os
import glob
import re
import json

# Caminhos base
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CAMINHO_JSON = os.path.join(DASHBOARD_DIR, "requests.json")
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
CAMINHO_MAPEAMENTO = os.path.join(BACKEND_DIR, "RACCL_lista_projetos.csv")

# Configurações de colunas
coluna_chave = "Def.projeto"
colunas_valores = [
    "Valor total em reais",
    "Val suj cont loc R$",
    "Valor cont local R$",
    "Estrangeiro $"
]

# Função auxiliar: limpeza de valores monetários
def limpar_valor(v):
    if pd.isna(v):
        return 0.0
    v = str(v).strip().replace("R$", "").replace(" ", "").replace(",", ".")
    v = re.sub(r"[^0-9.\-]", "", v)
    if v.count('.') > 1:
        partes = v.split('.')
        v = ''.join(partes[:-1]) + '.' + partes[-1]
    try:
        return float(v)
    except:
        return 0.0

# --- 1. Carrega mapeamento de projetos -> grupos ---
mapeamento = {}
if os.path.exists(CAMINHO_MAPEAMENTO):
    try:
        df_mapa = pd.read_csv(CAMINHO_MAPEAMENTO, sep=';', encoding='utf-8', dtype=str)
        df_mapa.columns = [c.strip() for c in df_mapa.columns]
        df_mapa = df_mapa.rename(columns={df_mapa.columns[0]: "Def.projeto", df_mapa.columns[1]: "Grupo"})
        for _, row in df_mapa.iterrows():
            mapeamento[row["Def.projeto"].strip()] = row["Grupo"].strip()
        print(f"Mapeamento carregado: {len(mapeamento)} entradas")
    except Exception as e:
        print("Erro ao ler RACCL_lista_projetos.csv:", e)
else:
    print(" Arquivo RACCL_lista_projetos.csv não encontrado.")
    df_mapa = pd.DataFrame(columns=["Def.projeto", "Grupo"])

# --- 2. Lê requests.json para obter diretórios ---
def obter_diretorios():
    if not os.path.exists(CAMINHO_JSON):
        return []
    try:
        with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, dict):
            caminhos = [dados.get("path")]
        elif isinstance(dados, list):
            caminhos = [d.get("path") for d in dados if "path" in d]
        else:
            caminhos = []
        return [c for c in caminhos if c and os.path.isdir(c)]
    except Exception as e:
        print("Erro ao ler requests.json:", e)
        return []

# --- 3. Processa os arquivos TXT ---
dfs = []

for BASE_DIR in obter_diretorios():
    for arquivo in glob.glob(os.path.join(BASE_DIR, "*.txt")):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                primeira_linha = f.readline()
            sep = ';' if ';' in primeira_linha else '\t'

            df = pd.read_csv(arquivo, sep=sep, encoding='utf-8', dtype=str)
            colunas_existentes = [c for c in colunas_valores if c in df.columns]
            if coluna_chave not in df.columns:
                continue

            for c in colunas_existentes:
                df[c] = df[c].apply(limpar_valor)

            dfs.append(df[[coluna_chave] + colunas_existentes])
        except Exception as e:
            print("Erro ao processar", arquivo, ":", e)

if not dfs:
    print("Nenhum arquivo processado.")
    exit()

# --- 4. Consolida dados individuais ---
df_total = pd.concat(dfs, ignore_index=True)
resultado = df_total.groupby(coluna_chave, as_index=False)[colunas_valores].sum()

# Adiciona coluna de grupo
resultado["Grupo"] = resultado[coluna_chave].map(mapeamento).fillna("OUTROS")

# --- 5. Agrupa por grupo ---
grupos = []
for grupo, df_g in resultado.groupby("Grupo"):
    soma = df_g[colunas_valores].sum(numeric_only=True)

    grupos.append({
        "grupo": grupo,
        "total": {col: soma[col] for col in colunas_valores},
        "itens": df_g.to_dict(orient="records")
    })

# --- 6. Salva em formato JSON hierárquico ---
with open(CAMINHO_JSON, "w", encoding="utf-8") as f:
    json.dump(grupos, f, ensure_ascii=False, indent=2)

print(f" JSON exportado com {len(grupos)} grupos em {CAMINHO_JSON}")
