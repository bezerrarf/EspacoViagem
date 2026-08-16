"""
====================================================================
MÓDULO DE REPOSITÓRIO DE ASTROS - ESPAÇO VIAGEM
====================================================================
Este módulo gerencia a leitura, estruturação, filtragem e busca de dados
dos corpos celestes a partir do arquivo 'models/astros.txt'.

Fornece métodos para:
1. Listar todos os astros catalogados.
2. Filtrar por categoria (Rochoso, Gigante Gasoso, Anão, Cometa, etc.).
3. Buscar astros por nome ou características.
4. Obter detalhes individuais para modais e visualizações.

Todos os nomes de funções, variáveis e comentários seguem o padrão em português.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

DIRETORIO_MODELS = Path(__file__).resolve().parent
CAMINHO_ARQUIVO_ASTROS = DIRETORIO_MODELS / "astros.txt"


def carregar_todos_os_astros() -> List[Dict[str, Any]]:
    """
    Lê o arquivo astros.txt e retorna uma lista de dicionários estruturados.
    Trata formatos de 5 a 8 colunas de forma retrocompatível.
    """
    if not CAMINHO_ARQUIVO_ASTROS.exists():
        print(f"[repositorio_astros] Arquivo não encontrado: {CAMINHO_ARQUIVO_ASTROS}")
        return []

    lista_astros: List[Dict[str, Any]] = []

    with open(CAMINHO_ARQUIVO_ASTROS, "r", encoding="utf-8") as arquivo:
        for indice, linha in enumerate(arquivo, start=1):
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("#"):
                continue

            partes = [p.strip() for p in linha_limpa.split("|")]
            
            # Suporta formato expandido (8 colunas) ou legado (5 colunas)
            if len(partes) >= 8:
                nome = partes[0]
                distancia = partes[1]
                massa = partes[2]
                categoria = partes[3]
                temperatura = partes[4]
                luas = partes[5]
                raio = partes[6]
                curiosidade = partes[7]
                url_imagem = partes[8] if len(partes) > 8 else "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=600"
            elif len(partes) >= 5:
                nome = partes[0]
                distancia = partes[1]
                massa = partes[2]
                categoria = inferir_categoria_por_nome(nome)
                temperatura = "Sob análise"
                luas = "Várias"
                raio = "Não especificado"
                curiosidade = partes[3]
                url_imagem = partes[4]
            else:
                continue

            # Gera slug/identificador único
            slug_astro = nome.lower().replace(" ", "-").replace("ú", "u").replace("ê", "e").replace("ã", "a")

            astro_estruturado = {
                "id": indice,
                "slug": slug_astro,
                "nome": nome,
                "distancia": distancia,
                "massa": massa,
                "categoria": categoria,
                "categoria_filtro": simplificar_categoria_filtro(categoria),
                "temperatura": temperatura,
                "luas": luas,
                "raio": raio,
                "curiosidade": curiosidade,
                "url_imagem": url_imagem
            }

            lista_astros.append(astro_estruturado)

    return lista_astros


def inferir_categoria_por_nome(nome: str) -> str:
    """
    Classifica automaticamente o astro caso o arquivo esteja em formato simplificado.
    """
    nome_baixo = nome.lower()
    if "sol" in nome_baixo:
        return "Estrela Central"
    elif any(p in nome_baixo for p in ["mercúrio", "mercurio", "vênus", "venus", "terra", "marte"]):
        return "Planeta Rochoso"
    elif any(p in nome_baixo for p in ["júpiter", "jupiter", "saturno"]):
        return "Gigante Gasoso"
    elif any(p in nome_baixo for p in ["urano", "netuno"]):
        return "Gigante de Gelo"
    elif "plutão" in nome_baixo or "plutao" in nome_baixo or "ceres" in nome_baixo:
        return "Planeta Anão"
    elif "lua" in nome_baixo:
        return "Satélite Natural"
    elif "cometa" in nome_baixo:
        return "Cometa Periódico"
    return "Corpo Celeste"


def simplificar_categoria_filtro(categoria: str) -> str:
    """
    Gera identificador de classe para filtros de botões na interface.
    """
    cat = categoria.lower()
    if "rochoso" in cat:
        return "rochosos"
    elif "gasoso" in cat or "gelo" in cat:
        return "gasosos"
    elif "anão" in cat or "anao" in cat:
        return "anoes"
    elif "cometa" in cat:
        return "cometas"
    elif "estrela" in cat:
        return "estrelas"
    return "outros"


def obter_astro_por_nome(nome_ou_slug: str) -> Optional[Dict[str, Any]]:
    """
    Retorna os dados completos de um astro específico pelo nome ou slug.
    """
    termo = nome_ou_slug.strip().lower()
    todos = carregar_todos_os_astros()
    for astro in todos:
        if astro["nome"].lower() == termo or astro["slug"] == termo:
            return astro
    return None


def filtrar_astros_por_categoria(categoria_filtro: str) -> List[Dict[str, Any]]:
    """
    Filtra a lista de astros pelo identificador de categoria.
    """
    todos = carregar_todos_os_astros()
    if not categoria_filtro or categoria_filtro == "todos":
        return todos
    return [a for a in todos if a["categoria_filtro"] == categoria_filtro.lower()]
