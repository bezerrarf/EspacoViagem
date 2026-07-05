from fasthtml.common import *
import sys
import os

# Pequeno truque para o Python achar a nossa pasta 'views'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from views.home import layout_pagina_inicial

# Inicializamos o aplicativo FastHTML
app, rt = fast_app()

# Criamos a rota principal (a página inicial do site: "/")
@rt('/')
def get():
    # Retornamos o título da aba do navegador e o layout que criamos na View
    return Title("Espaço Viagem"), layout_pagina_inicial()

# Ligamos o servidor!
serve()