from fasthtml.common import *
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from views.home import layout_pagina_inicial

# 1. FastHTML e CSS para funcionar!
app, rt = fast_app(
    hdrs=(Link(rel="stylesheet", href="/static/style.css"),)
)

# 2. Rota 
@rt('/static/{path:path}')
def arquivos_estaticos(path: str):
    return FileResponse(f'views/static/{path}')

@rt('/')
def get():
    return Title("Espaço Viagem"), layout_pagina_inicial()

serve()