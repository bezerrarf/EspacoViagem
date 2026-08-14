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

# 2.1: O motor do carrossel e avança 350 pixels a cada 10s.
script_carrossel = """
setInterval(function() {
    var trilho = document.querySelector('.trilho-carrossel');
    if (trilho) {
        // Se chegou no final, volta para o começo
        if (trilho.scrollLeft + trilho.clientWidth >= trilho.scrollWidth - 10) {
            trilho.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            // Se não, avança para o próximo cartão
            trilho.scrollBy({ left: 350, behavior: 'smooth' });
        }
    }
}, 5000);
"""

# 3. Em vez de criar um Link, enviar com força o CSS dentro de uma tag <style>!!!
app, rt = fast_app(
    pico=False,
    hdrs=(
        # 3.1: A tag que avisa aos celulares para adaptarem a tela
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Style(texto_do_css),
        # INCREMENTO 2: Injetando o motor do carrossel no site
        Script(script_carrossel)
    )
)

@rt('/')
def get():
    return Title("Espaço Viagem"), layout_pagina_inicial()

serve()
