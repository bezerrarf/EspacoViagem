from fasthtml.common import *
import os

def layout_pagina_inicial():
    
    # 1. MOCK DATA
    caminho_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_txt = os.path.join(caminho_atual, '..', 'models', 'astros.txt')
    
    arquivo = open(caminho_txt, "r", encoding="utf-8")
    linhas = arquivo.readlines()
    
    # 2. CARTÕES VISUAIS
    cartoes_visuais = []
    
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue # Pula caso haja alguma linha vazia no txt
            
        # Quebra a linha
        nome, distancia, massa, curiosidade, url_imagem = linha_limpa.split('|')
        
        # Desenha a caixa de informações do planeta
        cartao = Div(cls="cartao-planeta", *[
            Img(src=url_imagem, alt=f"Imagem de {nome}", cls="imagem-planeta"),
            Div(cls="info-planeta", *[
                H3(nome),
                P(Strong("Distância: "), distancia),
                P(Strong("Massa: "), massa),
                Hr(),
                P(curiosidade, cls="texto-curiosidade")
            ])
        ])
        
        cartoes_visuais.append(cartao)

    # 3. VISUAL
    return (
        # Cabeçalho do Menu
        Header(cls="top-bar", *[
            H1("🚀 Espaço Viagem", cls="logo"),
            Nav(cls="menu-principal", *[
                Ul(*[
                    Li(A("Início", href="/", cls="ativo")),
                    Li(A("Planetas", href="#")),
                    Li(A("Asteroides", href="#")),
                    Li(A("Sobre a Equipe", href="#"))
                ])
            ])
        ]),
        
        Main(cls="conteudo-principal", *[
            Section(cls="secao-carrossel", *[
                H2("Exploração Planetária", cls="titulo-secao"),
                Div(cls="trilho-carrossel", *cartoes_visuais)
            ]),

            Section(cls="secao-apresentacao", *[
                H2("Bem-vindo ao Cosmos!"),                
                P("Este é o ambiente inicial do projeto Espaço Viagem, desenvolvido por Ramon, Samira, Emmanuel e Pyerre."),
                P("Aqui vamos explorar imagens da NASA e dados da Wikipedia sobre o nosso sistema solar.")
            ])
        ]),
        
        Footer(cls="rodape-simples", *[
            P("© 2026 Projeto Espaço Viagem - Desenvolvido para estudos de programação e astronomia.")
        ])
    )