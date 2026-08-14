"""
nasa_api.py
Conexão e consumo da API da NASA — Imagem Astronômica do Dia (APOD).

Documentação oficial: https://api.nasa.gov/
"""

import os
import requests
from datetime import date
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (ex: NASA_API_KEY)
load_dotenv()

NASA_API_KEY = os.getenv("U3WRq4PbZ7LZFtAHt7s9WNhIqruOXrSeTTUKf7Mt")
URL_APOD = "https://api.nasa.gov/planetary/apod"

# Cache simples em memória: guarda a última resposta e a data em que foi buscada.
# Isso evita bater na API a cada request na home (a imagem do dia só muda 1x por dia).
_cache_apod = {
    "data_da_busca": None,
    "resultado": None,
}


def buscar_apod() -> dict | None:
    """
    Busca a Imagem Astronômica do Dia (APOD) na API da NASA.

    Retorna um dicionário com título, explicação, url da imagem e data,
    ou None se a busca falhar (API fora do ar, chave inválida, etc).
    """
    hoje = date.today()

    # Se já buscamos hoje, devolve o que está em cache
    if _cache_apod["data_da_busca"] == hoje and _cache_apod["resultado"] is not None:
        return _cache_apod["resultado"]

    if not NASA_API_KEY:
        print("[nasa_api] AVISO: NASA_API_KEY não encontrada. Verifique o arquivo .env")
        return None

    try:
        resposta = requests.get(
            URL_APOD,
            params={"api_key": NASA_API_KEY},
            timeout=10
        )
        resposta.raise_for_status()
    except requests.RequestException as erro:
        print(f"[nasa_api] Erro ao buscar APOD: {erro}")
        return None

    dados = resposta.json()

    # A API às vezes retorna um vídeo em vez de imagem (media_type == "video")
    if dados.get("media_type") != "image":
        return None

    resultado = {
        "titulo": dados.get("title"),
        "explicacao": dados.get("explanation"),
        "url_imagem": dados.get("url"),
        "data": dados.get("date"),
    }

    # Atualiza o cache
    _cache_apod["data_da_busca"] = hoje
    _cache_apod["resultado"] = resultado

    return resultado