from fasthtml.common import *
from pathlib import Path
import sys

# 1. Encontra a raiz
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ_PROJETO))

from views.home import layout_pagina_inicial

# 2. SOLUÇÃO: Ler o arquivo de texto do CSS diretamente para o Python!
caminho_css = RAIZ_PROJETO / "views" / "static" / "style.css"
texto_do_css = caminho_css.read_text(encoding="utf-8")

# 3. Em vez de criar um Link, enviar com força o CSS dentro de uma tag <style>!!!
app, rt = fast_app(
    pico=False,
    hdrs=(Style(texto_do_css),)
)

@rt('/')
def get():
    return Title("Espaço Viagem"), layout_pagina_inicial()

serve()
