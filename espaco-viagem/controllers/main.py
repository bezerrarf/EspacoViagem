from fasthtml.common import *
import sys
import os

# Para localizar a pasta 'views'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from views.home import layout_pagina_inicial

# Inicializando o FastHTML
app, rt = fast_app()

# Criamos a rota principal ( "/" )
@rt('/')
def get():
    # Retorna o título da aba do navegador e o layout da View
    return Title("Espaço Viagem"), layout_pagina_inicial()

# Servidor on!!
serve()