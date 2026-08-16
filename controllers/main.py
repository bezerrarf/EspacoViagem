"""
====================================================================
CONTROLADOR PRINCIPAL (MAIN.PY) - PROJETO ESPAÇO VIAGEM
====================================================================
Este módulo é o coração da aplicação backend:
1. Inicializa o servidor FastHTML/Starlette.
2. Injeta CSS Dark Cósmico e JavaScripts diretamente nos templates HTML.
3. Entrega os arquivos HTML puros da pasta 'views/' preenchidos dinamicamente.
4. Fornece endpoints de API REST JSON para:
   - Busca Cósmica Unificada (NASA + Wikipedia).
   - Cadastro e Login de Usuários com Perfis (Admin, Professor, Estudante).
   - Histórico de Buscas e Auditoria de Logins no SQLite.
   - Gerenciamento e Limpeza de Caches.

Todos os nomes de funções, variáveis e comentários seguem o padrão em português.
"""

from fasthtml.common import *
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from pathlib import Path
import sys
import os

# 1. Configuração do caminho raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ_PROJETO))

# 2. Importação dos modelos e conexões com APIs
from models.banco_de_dados import (
    cadastrar_usuario,
    autenticar_usuario,
    registrar_log_login,
    listar_historico_logins,
    salvar_busca_usuario,
    listar_historico_buscas_usuario,
    limpar_historico_buscas_usuario,
    limpar_todos_caches,
    obter_estatisticas_gerais
)
from models.nasa_api import buscar_apod, buscar_imagens_nasa, buscar_asteroides_proximos
from models.wikipedia_api import buscar_resumo_wikipedia
from models.repositorio_astros import carregar_todos_os_astros

# 3. Caminhos das pastas estáticas e templates HTML
DIRETORIO_VIEWS = RAIZ_PROJETO / "views"
DIRETORIO_STATIC = RAIZ_PROJETO / "views" / "static"

# 4. Inicialização do FastHTML
app, rt = fast_app(
    pico=False,
    hdrs=(
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Ambiente educacional de exploração cósmica com dados da NASA e Wikipedia."),
        Title("Espaço Viagem — Exploração Cósmica")
    )
)

# 5. Montagem dos arquivos estáticos (/static/css, /static/js, /static/imagens)
if DIRETORIO_STATIC.exists():
    app.mount("/static", StaticFiles(directory=str(DIRETORIO_STATIC)), name="static")


def carregar_conteudo_estatico() -> dict:
    """
    Lê o CSS e os scripts JS para injeção direta no HTML,
    garantindo que o tema dark e as animações NUNCA falhem ao carregar.
    """
    caminho_css = DIRETORIO_STATIC / "css" / "style.css"
    caminho_busca_js = DIRETORIO_STATIC / "js" / "busca_cosmica.js"
    caminho_carrossel_js = DIRETORIO_STATIC / "js" / "carrossel.js"
    caminho_auth_js = DIRETORIO_STATIC / "js" / "autenticacao.js"

    texto_css = caminho_css.read_text(encoding="utf-8") if caminho_css.exists() else ""
    texto_busca_js = caminho_busca_js.read_text(encoding="utf-8") if caminho_busca_js.exists() else ""
    texto_carrossel_js = caminho_carrossel_js.read_text(encoding="utf-8") if caminho_carrossel_js.exists() else ""
    texto_auth_js = caminho_auth_js.read_text(encoding="utf-8") if caminho_auth_js.exists() else ""

    return {
        "css": texto_css,
        "busca_js": texto_busca_js,
        "carrossel_js": texto_carrossel_js,
        "auth_js": texto_auth_js
    }


def carregar_template_html(nome_arquivo: str) -> str:
    """
    Lê o conteúdo textual de um arquivo HTML puro dentro da pasta views
    e injeta o CSS e scripts protegidos.
    """
    caminho_arquivo = DIRETORIO_VIEWS / nome_arquivo
    if not caminho_arquivo.exists():
        return f"<h1>Erro: Arquivo {nome_arquivo} não encontrado na pasta views.</h1>"

    conteudo_html = caminho_arquivo.read_text(encoding="utf-8")
    ativos = carregar_conteudo_estatico()

    return (
        conteudo_html
        .replace("{{ estilo_css_embutido }}", ativos["css"])
        .replace("{{ script_busca_js }}", ativos["busca_js"])
        .replace("{{ script_carrossel_js }}", ativos["carrossel_js"])
        .replace("{{ script_auth_js }}", ativos["auth_js"])
    )


def extrair_termo_astronomico_relevante(titulo: str, explicacao: str) -> str:
    """
    Identifica o principal objeto ou conceito astronômico no título/explicação
    para buscar o resumo correto na Wikipedia em português.
    """
    texto_completo = f"{titulo} {explicacao}".lower()

    mapa_termos = {
        "perseid": "Perseidas",
        "meteor": "Meteoro",
        "eclipse": "Eclipse",
        "solar": "Sol",
        "sun": "Sol",
        "moon": "Lua",
        "mars": "Marte",
        "jupiter": "Júpiter",
        "saturn": "Saturno",
        "venus": "Vênus",
        "mercury": "Mercúrio",
        "uranus": "Urano",
        "neptune": "Netuno",
        "pluto": "Plutão",
        "nebula": "Nebulosa",
        "galaxy": "Galáxia",
        "comet": "Cometa",
        "aurora": "Aurora polar",
        "supernova": "Supernova",
        "black hole": "Buraco negro",
        "milky way": "Via Láctea",
        "james webb": "Telescópio Espacial James Webb",
        "hubble": "Telescópio Espacial Hubble"
    }

    for chave, termo_traduzido in mapa_termos.items():
        if chave in texto_completo:
            return termo_traduzido

    return "Astronomia"


# ====================================================================
# ROTAS DE PÁGINAS (DELIVERY DE HTML PURO)
# ====================================================================

@rt('/')
def get_inicio():
    """
    Entrega a página inicial (views/index.html) com busca central,
    APOD enriquecido com Wikipedia, carrossel e radar de asteroides.
    """
    template_html = carregar_template_html("index.html")

    # 1. Consulta APOD da NASA e Resumo Inteligente na Wikipedia
    dados_apod = buscar_apod()
    termo_astronomico = extrair_termo_astronomico_relevante(
        dados_apod.get("titulo", ""),
        dados_apod.get("explicacao", "")
    )
    dados_wiki_apod = buscar_resumo_wikipedia(termo_astronomico)

    # 2. Carrega todos os astros para o carrossel
    lista_astros = carregar_todos_os_astros()
    cartoes_astros = []
    for astro in lista_astros:
        cartao_html = f"""
        <div class="cartao-astro">
            <div class="container-imagem-astro">
                <img src="{astro['url_imagem']}" alt="{astro['nome']}" class="imagem-astro" onerror="this.src='https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=600'">
            </div>
            <div class="corpo-astro">
                <span class="badge-nasa" style="width: fit-content;">{astro['categoria']}</span>
                <h3 class="nome-astro">{astro['nome']}</h3>
                <div class="metricas-astro">
                    <div><strong>Distância:</strong> {astro['distancia']}</div>
                    <div><strong>Massa:</strong> {astro['massa']}</div>
                </div>
                <p style="color: #94a3b8; font-size: 0.86rem; line-height: 1.5;">{astro['curiosidade']}</p>
            </div>
        </div>
        """
        cartoes_astros.append(cartao_html)

    # 3. Carrega os asteroides próximos (NeoWs)
    lista_asteroides = buscar_asteroides_proximos()
    cartoes_asteroides = []
    for ast in lista_asteroides:
        classe_badge = "badge-wiki" if not ast.get("perigoso") else "badge-nasa"
        texto_perigo = "Órbita Segura" if not ast.get("perigoso") else "Atenção: Monitoramento"

        cartao_ast_html = f"""
        <div class="cartao-astro">
            <div class="corpo-astro">
                <span class="{classe_badge}" style="width: fit-content;">{texto_perigo}</span>
                <h3 class="nome-astro" style="margin-top: 0.5rem;">{ast['nome']}</h3>
                <div style="font-size: 0.85rem; color: #cbd5e1; display: flex; flex-direction: column; gap: 0.3rem;">
                    <div><strong>Diâmetro Estimado:</strong> {ast['diametro_metros']} metros</div>
                    <div><strong>Velocidade:</strong> {ast['velocidade_km_h']} km/h</div>
                    <div><strong>Distância da Terra:</strong> {ast['distancia_km']} km</div>
                    <div><strong>Aproximação:</strong> {ast['data_aproximacao']}</div>
                </div>
            </div>
        </div>
        """
        cartoes_asteroides.append(cartao_ast_html)

    # 4. Substituição das tags no template HTML
    html_final = (
        template_html
        .replace("{{ apod.titulo }}", dados_apod.get("titulo", "Visão Cósmica"))
        .replace("{{ apod.data }}", dados_apod.get("data", ""))
        .replace("{{ apod.origem_dados }}", dados_apod.get("origem_dados", "NASA"))
        .replace("{{ apod.explicacao }}", dados_apod.get("explicacao", ""))
        .replace("{{ apod.url_imagem }}", dados_apod.get("url_imagem", ""))
        .replace("{{ resumo_wiki_apod.titulo }}", dados_wiki_apod.get("titulo", termo_astronomico))
        .replace("{{ resumo_wiki_apod.resumo }}", dados_wiki_apod.get("resumo", "Resumo científico astronômico."))
        .replace("{{ resumo_wiki_apod.url_pagina_completa }}", dados_wiki_apod.get("url_pagina_completa", "#"))
        .replace("{{ cartoes_astros_html }}", "\n".join(cartoes_astros))
        .replace("{{ cartoes_asteroides_html }}", "\n".join(cartoes_asteroides))
    )

    return HTMLResponse(html_final)


@rt('/cadastro')
def get_cadastro():
    """Entrega a tela de cadastro (views/cadastro.html)."""
    template_html = carregar_template_html("cadastro.html")
    return HTMLResponse(template_html)


@rt('/login')
def get_login():
    """
    Entrega a tela de login (views/login.html) com preenchimento
    do histórico de buscas salvas e registros de auditoria do SQLite.
    """
    template_html = carregar_template_html("login.html")

    # 1. Carrega histórico de buscas salvas do SQLite
    historico_buscas = listar_historico_buscas_usuario(2, limite=10)
    linhas_buscas = []
    if historico_buscas:
        for b in historico_buscas:
            linhas_buscas.append(f"""
                <tr>
                    <td><strong>{b['termo_pesquisado']}</strong></td>
                    <td><span class="badge-wiki">{b['categoria_resultado']}</span></td>
                    <td>{b['total_resultados']} itens</td>
                    <td>{b['data_hora_busca']}</td>
                </tr>
            """)
    else:
        linhas_buscas.append("<tr><td colspan='4' style='text-align:center; color:#64748b;'>Nenhuma busca salva no histórico.</td></tr>")

    # 2. Carrega logs de auditoria de login para o Administrador
    logs_login = listar_historico_logins(limite=10)
    linhas_logins = []
    for log in logs_login:
        cor_status = "#34d399" if log["status"] == "SUCESSO" else "#f87171"
        linhas_logins.append(f"""
            <tr>
                <td>{log['data_hora']}</td>
                <td>{log['email_tentativa']}</td>
                <td><span class="badge-nasa">{log['papel']}</span></td>
                <td><strong style="color: {cor_status};">{log['status']}</strong></td>
                <td>{log['endereco_ip']}</td>
            </tr>
        """)

    html_final = (
        template_html
        .replace("{{ linhas_historico_buscas_html }}", "\n".join(linhas_buscas))
        .replace("{{ linhas_auditoria_logins_html }}", "\n".join(linhas_logins))
    )
    return HTMLResponse(html_final)


@rt('/planetas')
def get_planetas():
    """Entrega a galeria completa de planetas (views/planetas.html)."""
    template_html = carregar_template_html("planetas.html")
    todos_astros = carregar_todos_os_astros()

    cartoes_html = []
    for astro in todos_astros:
        resumo_wiki = buscar_resumo_wikipedia(astro["nome"])
        cartoes_html.append(f"""
        <div class="cartao-astro">
            <div class="container-imagem-astro">
                <img src="{astro['url_imagem']}" alt="{astro['nome']}" class="imagem-astro" onerror="this.src='https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=600'">
            </div>
            <div class="corpo-astro">
                <span class="badge-nasa" style="width: fit-content;">{astro['categoria']}</span>
                <h3 class="nome-astro">{astro['nome']}</h3>
                <div class="metricas-astro">
                    <div><strong>Distância:</strong> {astro['distancia']}</div>
                    <div><strong>Massa:</strong> {astro['massa']}</div>
                </div>
                <p style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.5; margin-top: 0.5rem;">
                    <strong style="color: #f59e0b;">Wikipedia:</strong> {resumo_wiki['resumo'][:160]}...
                </p>
                <a href="{resumo_wiki['url_pagina_completa']}" target="_blank" style="color: #38bdf8; font-size: 0.8rem; font-weight: 600; margin-top: auto;">Artigo completo na Wikipedia →</a>
            </div>
        </div>
        """)

    html_final = template_html.replace("{{ cartoes_todos_astros_html }}", "\n".join(cartoes_html))
    return HTMLResponse(html_final)


@rt('/sobre')
def get_sobre():
    """Entrega a tela Sobre a Equipe (views/sobre.html)."""
    template_html = carregar_template_html("sobre.html")
    return HTMLResponse(template_html)


# ====================================================================
# ROTAS DE API REST JSON (CONSUMO VIA JAVASCRIPT)
# ====================================================================

@rt('/api/busca')
def get_api_busca(termo: str = "", usuario_id: str = "", pagina: int = 1):
    """
    Endpoint de Busca Cósmica Integrada com Paginação:
    1. Consulta fotos e missões na NASA Image Library (12 por página).
    2. Consulta o resumo científico na Wikipedia em português.
    3. Suporta paginação pelo parâmetro 'pagina' para o botão 'Ver Mais'.
    4. Se houver usuário_id autenticado, salva no histórico do SQLite.
    """
    termo_limpo = termo.strip()
    if not termo_limpo:
        return JSONResponse({"sucesso": False, "mensagem": "Nenhum termo informado."})

    # 1. Calcula quantas imagens buscar (12 por página, acumulando)
    imagens_por_pagina = 12
    total_buscar = imagens_por_pagina * pagina

    # 2. Busca todas as imagens e fatia a página correta
    todos_resultados = buscar_imagens_nasa(termo_limpo, limite=total_buscar)
    inicio = (pagina - 1) * imagens_por_pagina
    resultados_pagina = todos_resultados[inicio:total_buscar]

    # 3. Resumo Wikipedia (apenas na primeira página)
    resumo_wiki = buscar_resumo_wikipedia(termo_limpo) if pagina == 1 else None

    # 4. Verifica se há mais imagens disponíveis
    tem_mais = len(todos_resultados) == total_buscar

    # 5. Gravação de histórico se for usuário autenticado
    if usuario_id and usuario_id.isdigit() and pagina == 1:
        id_int = int(usuario_id)
        salvar_busca_usuario(id_int, termo_limpo, "Astronomia", len(todos_resultados))

    return JSONResponse({
        "sucesso": True,
        "termo": termo_limpo,
        "resultados_nasa": resultados_pagina,
        "wikipedia": resumo_wiki,
        "pagina_atual": pagina,
        "tem_mais": tem_mais
    })


@rt('/api/cadastrar')
async def post_api_cadastrar(request):
    """Processa formulário de cadastro e insere no banco SQLite."""
    form_data = await request.form()
    nome = form_data.get("nome", "")
    email = form_data.get("email", "")
    senha = form_data.get("senha", "")
    papel = form_data.get("papel", "ESTUDANTE")

    resultado = cadastrar_usuario(nome, email, senha, papel)
    return JSONResponse(resultado)


@rt('/api/login')
async def post_api_login(request):
    """Valida login, autentica o usuário e grava registro de auditoria."""
    form_data = await request.form()
    email = form_data.get("email", "")
    senha = form_data.get("senha", "")

    usuario = autenticar_usuario(email, senha)
    ip_cliente = request.client.host if request.client else "127.0.0.1"
    navegador = request.headers.get("user-agent", "Web Browser")[:50]

    if usuario:
        registrar_log_login(email, "SUCESSO", ip_cliente, navegador, usuario["id"], usuario["papel"])
        return JSONResponse({
            "sucesso": True,
            "mensagem": f"Login realizado com sucesso! Olá, {usuario['nome_completo']}.",
            "usuario": usuario
        })
    else:
        registrar_log_login(email, "FALHA", ip_cliente, navegador, None, "VISITANTE")
        return JSONResponse({
            "sucesso": False,
            "mensagem": "Credenciais incorretas. Verifique seu e-mail e senha."
        })


@rt('/api/usuario/historico')
def delete_api_historico(usuario_id: int):
    """Limpa o histórico de pesquisas de um usuário autenticado."""
    sucesso = limpar_historico_buscas_usuario(usuario_id)
    return JSONResponse({"sucesso": sucesso, "mensagem": "Histórico de pesquisas limpo com sucesso."})


@rt('/api/caches/limpar')
def post_api_limpar_caches():
    """Função exclusiva do Administrador para limpar caches do SQLite."""
    total_removidos = limpar_todos_caches()
    return JSONResponse({
        "sucesso": True,
        "mensagem": f"Foram limpos {total_removidos} registros de cache do banco de dados."
    })


# 6. Inicialização do servidor
if __name__ == "__main__":
    porta = int(os.getenv("PORTA", 5001))
    print(f"\n========================================================")
    print(f"🚀 SERVIDOR ESPAÇO VIAGEM EM EXECUÇÃO!")
    print(f"📡 Acesse no seu navegador: http://localhost:{porta}")
    print(f"========================================================\n")
    serve(port=porta)
git status