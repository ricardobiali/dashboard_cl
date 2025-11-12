import eel
import json
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
import ctypes
import win32gui
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
REQUESTS_JSON = BASE_DIR / "requests.json"
BACKEND_DIR = BASE_DIR / "backend"
READ_FILES_PY = BACKEND_DIR / "read_files.py"

# Inicializa o Eel apontando para o frontend
eel.init(str(FRONTEND_DIR))

# SELETOR DE DIRETÓRIO
tk_root = None
@eel.expose
def selecionar_diretorio():
    """
    Abre um diálogo para o usuário escolher um diretório e retorna o caminho.
    """
    global tk_root
    try:
        if tk_root is None:
            tk_root = tk.Tk()
            tk_root.withdraw()

        try:
            hwnd_main = win32gui.GetForegroundWindow()
        except Exception:
            hwnd_main = None

        if hwnd_main:
            try:
                tk_root.wm_attributes("-toolwindow", True)
                tk_root.wm_attributes("-topmost", True)
                tk_root.lift()
                tk_root.focus_force()
                ctypes.windll.user32.SetWindowLongW(
                    tk_root.winfo_id(),
                    -8,
                    hwnd_main
                )
            except Exception as e:
                print("Aviso: não foi possível vincular janela Tk ao app principal:", e)

        folder_selected = filedialog.askdirectory(
            parent=tk_root,
            title="Selecione um diretório de armazenamento"
        )
        print("selecionar_diretorio ->", folder_selected)
        return folder_selected if folder_selected else ""

    except Exception as e:
        print("Erro ao abrir diálogo de pasta:", e)
        return ""

#  SALVAR CAMINHO + EXECUTAR MACRO
@eel.expose
def salvar_caminho(caminho_rede: str):
    try:
        if not caminho_rede or not caminho_rede.strip():
            return {"status": "erro", "mensagem": "Caminho de rede vazio."}

        caminho_rede = os.path.normpath(caminho_rede.strip())

        dados_existentes = []
        if REQUESTS_JSON.exists():
            try:
                with open(REQUESTS_JSON, "r", encoding="utf-8") as f:
                    dados_existentes = json.load(f)
                    if not isinstance(dados_existentes, list):
                        dados_existentes = [dados_existentes]
            except (json.JSONDecodeError, ValueError):
                print(" requests.json inválido — recriando do zero.")
                dados_existentes = []

        caminhos_existentes = [os.path.normpath(item.get("path", "")) for item in dados_existentes]
        if caminho_rede not in caminhos_existentes:
            dados_existentes.append({"path": caminho_rede})
            print(f" Caminho adicionado: {caminho_rede}")
        else:
            print(f" Caminho já existe em requests.json: {caminho_rede}")

        with open(REQUESTS_JSON, "w", encoding="utf-8") as f:
            json.dump(dados_existentes, f, ensure_ascii=False, indent=2)

        print(f" requests.json atualizado:\n{json.dumps(dados_existentes, indent=2, ensure_ascii=False)}")

        if READ_FILES_PY.exists():
            print(f"Executando {READ_FILES_PY} ...")
            subprocess.run(
                ["python", str(READ_FILES_PY)],
                cwd=str(BACKEND_DIR),
                check=True
            )
            print("Macro executada com sucesso.")
        else:
            print(" Arquivo read_files.py não encontrado.")

        return {"status": "ok", "mensagem": "Caminho salvo e macro executada com sucesso."}

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar macro: {e}")
        return {"status": "erro", "mensagem": f"Erro ao executar macro: {e}"}
    except Exception as e:
        print(f"Erro ao salvar caminho: {e}")
        return {"status": "erro", "mensagem": str(e)}

#  CARREGAR DADOS
@eel.expose
def carregar_dados():
    try:
        with open(REQUESTS_JSON, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, dict):
                dados = [dados]
        return dados
    except FileNotFoundError:
        return []
    except Exception as e:
        print("Erro ao carregar dados:", e)
        return []

#  INICIALIZAÇÃO DO EEL
if __name__ == "__main__":
    try:
        eel.start(
            "index.html",
            port=0,
            size=(1200, 800),
            cmdline_args=['--start-maximized']
        )
    except OSError:
        eel.start(
            "index.html",
            port=8080,
            size=(1200, 800),
            cmdline_args=['--start-maximized']
        )
