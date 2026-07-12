from fasthtml.common import *

def layout_pagina_inicial():
    
    # 1. ABRINDO OS MOCK DATA 
    arquivo = open("models/astros.txt", "r", encoding="utf-8")
    linhas = arquivo.readlines()
    
    # 2. PREPARANDO OS CARTÕES VISUAIS
    cartoes_visuais = []
    
    for linha in linhas:
        # Leitura da quebra a linha, onde tem a barra (|) he guarda nas variáveis
        nome, distancia, massa, curiosidade = linha.split('|')
        
        # Desenha a caixa de informações do planeta
        cartao = Div(cls="cartao-planeta", *[
            Div("NASA IMAGE PLACEHOLDER", cls="placeholder-img"),
            Div(cls="info-planeta", *[
                H3(nome),
                P(Strong("Distância: "), distancia),
                P(Strong("Massa: "), massa),
                Hr(),
                P(curiosidade, cls="texto-curiosidade")
            ])
        ])
        
        # Adiciona o cartão da lista
        cartoes_visuais.append(cartao)

    # 3. MONTANDO O VISUAL
    return (
        # Cabeçalho
        Header(cls="top-bar", *[
            H1("🚀 Espaço Viagem", cls="logo"),
            Nav(cls="menu-principal", *[
                Ul(
                    Li(A("Início", href="/", cls="ativo")),
                    Li(A("Planetas", href="#")),
                    Li(A("Asteroides", href="#")),
                    Li(A("Sobre a Equipe", href="#"))
                )
            ])
        ]),
        
        # Conteúdo Principal
        Main(cls="conteudo-principal", *[
            Section(cls="secao-apresentacao", *[
                H2("Bem-vindo ao Cosmos!"),
                P("Este é o ambiente inicial do projeto Espaço Viagem, desenvolvido por Ramon, Samira, Emmanuel e Pyerre."),
                P("Aqui vamos explorar imagens da NASA e dados da Wikipedia sobre o nosso sistema solar.")
            ]),
            
            Section(cls="secao-carrossel", *[
                H2("Exploração Planetária", cls="titulo-secao"),
                
                # Despejando todos os cartões criados em cima aqui
                Div(cls="trilho-carrossel", *cartoes_visuais)
            ])
        ]),
        
        # Rodapé
        Footer(cls="rodape-simples", *[
            P("© 2026 Projeto Espaço Viagem - Desenvolvido para estudos de programação e astronomia.")
        ])
    )
