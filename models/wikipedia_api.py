"""
====================================================================
MÓDULO DE INTEGRAÇÃO COM A WIKIPEDIA (RESUMOS CIENTÍFICOS)
====================================================================
Consulta a API oficial da Wikipedia em português para retornar
resumos astronômicos precisos. Possui mapeamento direto para evitar
páginas de desambiguação (ex: "Marte" → "Marte (planeta)").

Todos os nomes de funções, variáveis e comentários seguem o padrão em português.
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any

# Carrega as variáveis do arquivo .env
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ_PROJETO / ".env")

from models.banco_de_dados import obter_cache, salvar_cache

# Configurações do .env
URL_WIKIPEDIA_RESUMO = os.getenv("URL_WIKIPEDIA_RESUMO", "https://pt.wikipedia.org/api/rest_v1/page/summary/")
URL_WIKIPEDIA_BUSCA = os.getenv("URL_WIKIPEDIA_BUSCA", "https://pt.wikipedia.org/w/api.php")
IDIOMA_WIKIPEDIA = os.getenv("IDIOMA_WIKIPEDIA", "pt")

CABECALHOS_HTTP = {
    "User-Agent": "EspacoViagem/pt (https://github.com/samir/EspacoViagem-Visual; projeto educacional)"
}

# Mapeamento direto de termos para os artigos CORRETOS da Wikipedia em PT
# Evita páginas de desambiguação e artigos errados
MAPA_ARTIGOS_WIKIPEDIA = {
    # Planetas do Sistema Solar
    "marte":               "Marte_(planeta)",
    "júpiter":             "Júpiter_(planeta)",
    "jupiter":             "Júpiter_(planeta)",
    "saturno":             "Saturno_(planeta)",
    "vênus":               "Vénus_(planeta)",
    "venus":               "Vénus_(planeta)",
    "mercúrio":            "Mercúrio_(planeta)",
    "mercurio":            "Mercúrio_(planeta)",
    "urano":               "Urano_(planeta)",
    "netuno":              "Netuno_(planeta)",
    "plutão":              "Plutão_(planeta_anão)",
    "plutao":              "Plutão_(planeta_anão)",
    "terra":               "Terra",
    "lua":                 "Lua",
    "sol":                 "Sol",
    # Objetos e Fenômenos
    "buraco negro":        "Buraco_negro",
    "buracos negros":      "Buraco_negro",
    "nebulosa":            "Nebulosa",
    "nebulosa de órion":   "Nebulosa_de_Órion",
    "via láctea":          "Via_Láctea",
    "via lactea":          "Via_Láctea",
    "galáxia":             "Galáxia",
    "galaxia":             "Galáxia",
    "estrela":             "Estrela",
    "cometa":              "Cometa",
    "cometa halley":       "Cometa_Halley",
    "asteroide":           "Asteroide",
    "asteroides":          "Asteroide",
    "meteoro":             "Meteoro",
    "perseidas":           "Perseidas",
    "aurora boreal":       "Aurora_boreal",
    "supernova":           "Supernova",
    "estrela de nêutrons": "Estrela_de_nêutrons",
    "anã branca":          "Anã_branca",
    "quasar":              "Quasar",
    "exoplaneta":          "Exoplaneta",
    "eclipse solar":       "Eclipse_solar",
    "eclipse lunar":       "Eclipse_lunar",
    # Telescópios e Missões
    "james webb":          "Telescópio_Espacial_James_Webb",
    "hubble":              "Telescópio_Espacial_Hubble",
    "voyager":             "Programa_Voyager",
    "curiosity":           "Curiosity_(sonda_espacial)",
    "perseverance":        "Perseverance_(sonda_espacial)",
    # Astronomia geral
    "astronomia":          "Astronomia",
    "universo":            "Universo",
    "sistema solar":       "Sistema_Solar",
    "cosmos":              "Cosmos",
}


def buscar_resumo_wikipedia(termo_busca: str) -> Dict[str, Any]:
    """
    Busca o resumo científico na Wikipedia em português.
    Usa mapeamento direto para evitar páginas de desambiguação.

    Fluxo:
    1. Normaliza o termo e verifica cache no SQLite.
    2. Mapeia para o artigo correto da Wikipedia (sem desambiguação).
    3. Faz a requisição para a API REST da Wikipedia.
    4. Salva no SQLite por 7 dias (168 horas).
    """
    termo_limpo = termo_busca.strip()
    if not termo_limpo:
        return {
            "titulo": "Exploração Espacial",
            "resumo": "O universo abriga bilhões de galáxias, estrelas e planetas esperando por descobertas.",
            "url_imagem_wiki": None,
            "url_pagina_completa": f"https://pt.wikipedia.org/wiki/Astronomia",
            "origem": "Wikipedia (Padrão)"
        }

    chave_cache = f"wiki_v2_{termo_limpo.lower().replace(' ', '_')}"

    # 1. Tenta recuperar do cache
    cache_local = obter_cache(chave_cache)
    if cache_local:
        cache_local["origem"] = "Cache Local SQLite (Wikipedia)"
        return cache_local

    # 2. Resolve o artigo correto via mapeamento direto
    termo_normalizado = termo_limpo.lower().strip()
    artigo_wikipedia = MAPA_ARTIGOS_WIKIPEDIA.get(
        termo_normalizado,
        termo_limpo.replace(" ", "_")
    )

    # 3. Busca na API REST da Wikipedia
    resultado = _buscar_artigo_wikipedia(artigo_wikipedia, termo_limpo)

    # 4. Se não encontrou com o mapeamento, tenta a busca full-text
    if not resultado:
        resultado = _buscar_fulltext_wikipedia(termo_limpo)

    if resultado:
        salvar_cache(chave_cache, "wikipedia_v2", resultado, duracao_horas=168)
        return resultado

    # 5. Fallback de contingência
    return {
        "titulo": termo_limpo.title(),
        "resumo": f"Objeto astronômico fascinante: {termo_limpo}. Acesse a Wikipedia para saber mais.",
        "url_imagem_wiki": None,
        "url_pagina_completa": f"https://pt.wikipedia.org/wiki/{artigo_wikipedia}",
        "origem": "Wikipedia (Acervo Offline)"
    }


def _buscar_artigo_wikipedia(slug_artigo: str, termo_original: str) -> Dict[str, Any] | None:
    """
    Busca um artigo específico da Wikipedia pelo seu slug (nome do artigo na URL).
    Retorna None se não encontrar.
    """
    url_final = f"{URL_WIKIPEDIA_RESUMO}{slug_artigo}"

    try:
        resposta = requests.get(url_final, headers=CABECALHOS_HTTP, timeout=6)

        if resposta.status_code == 200:
            dados = resposta.json()

            # Descarta páginas de desambiguação
            tipo_pagina = dados.get("type", "")
            if tipo_pagina == "disambiguation":
                return None

            resumo = dados.get("extract") or dados.get("description") or ""
            if not resumo:
                return None

            return {
                "titulo": dados.get("title", termo_original),
                "resumo": resumo,
                "url_imagem_wiki": dados.get("thumbnail", {}).get("source"),
                "url_pagina_completa": (
                    dados.get("content_urls", {}).get("desktop", {}).get("page")
                    or f"https://pt.wikipedia.org/wiki/{slug_artigo}"
                ),
                "origem": "Wikipedia Oficial (pt)"
            }

    except Exception as erro:
        print(f"[wikipedia_api] Erro ao buscar artigo '{slug_artigo}': {erro}")

    return None


def _buscar_fulltext_wikipedia(termo: str) -> Dict[str, Any] | None:
    """
    Busca pelo texto completo na Wikipedia quando o artigo direto não é encontrado.
    Ignora automaticamente páginas de desambiguação nos resultados.
    """
    parametros = {
        "action": "query",
        "list": "search",
        "srsearch": f"{termo} astronomia espaço",  # Contextualiza para astronomia
        "format": "json",
        "utf8": 1,
        "srlimit": 5
    }

    try:
        resposta = requests.get(URL_WIKIPEDIA_BUSCA, params=parametros, headers=CABECALHOS_HTTP, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            resultados = dados.get("query", {}).get("search", [])

            for resultado in resultados:
                titulo_encontrado = resultado.get("title", "")

                # Ignora artigos de desambiguação
                if "(desambiguação)" in titulo_encontrado.lower():
                    continue

                slug = titulo_encontrado.replace(" ", "_")
                artigo = _buscar_artigo_wikipedia(slug, titulo_encontrado)
                if artigo:
                    return artigo

    except Exception as erro:
        print(f"[wikipedia_api] Erro na busca full-text: {erro}")

    return None
