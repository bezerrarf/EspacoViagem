from fasthtml.common import *

def layout_pagina_inicial():
    # Retorna as partes principais que compõem o corpo do site
    return (
        # 1. CABEÇALHO E NAVEGAÇÃO
        Header(
            H1("🚀 Espaço Viagem 🚀"),
            Nav(
                Ul(
                    Li(A("Início", href="/")),
                    Li(A("Planetas (Em breve)", href="#")),
                    Li(A("Asteroides (Em breve)", href="#")),
                    Li(A("Sobre a Equipe", href="#"))
                )
            )
        ),
        
        # 2. CONTEÚDO PRINCIPAL
        Main(
            # Seção 1: Apresentação
            Section(
                H2("Bem-vindo ao Cosmos!"),
                P("Este é o ambiente inicial do projeto Espaço Viagem, desenvolvido por Ramon, Samira, Emmanuel e Pyerre."),
                P("Aqui vamos explorar imagens da NASA e dados da Wikipedia sobre o nosso sistema solar.")
            ),
            
            # Seção 2: Espaço reservado...
            Section(
                H2("Imagem Astronômica do Dia"),
                P("Em breve, este espaço receberá os dados integrados da API da NASA.")
            )
        ),
        
        # 3. RODAPÉ
        Footer(
            P("© 2026 Projeto Espaço Viagem - Desenvolvido para estudos de programação e astronomia.")
        )
    )


