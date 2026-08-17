"""
====================================================================
MÓDULO DE BANCO DE DADOS - ESPAÇO VIAGEM
====================================================================
Este módulo gerencia toda a camada de persistência local SQLite:
1. Armazenamento e consulta de Caches das APIs (NASA e Wikipedia).
2. Cadastro e autenticação de usuários nos perfis:
   - ADMINISTRADOR: Acesso a relatórios de auditoria e controle de caches.
   - PROFESSOR: Acesso a histórico de pesquisas e resumos didáticos.
   - ESTUDANTE: Exploração e buscas com histórico pessoal.
3. Registro de auditoria de acessos e logins (IP, data/hora, status, navegador).
4. Gravação de histórico de buscas astronômicas personalizadas.

Todos os nomes de funções, variáveis e comentários seguem o padrão em português.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

# Caminho absoluto para o arquivo de banco de dados SQLite local
DIRETORIO_MODELS = Path(__file__).resolve().parent
CAMINHO_BANCO_DADOS = DIRETORIO_MODELS / "espaco_viagem.db"


def obter_conexao() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão ativa com o banco de dados SQLite.
    Configura row_factory para permitir acesso aos campos por nome de coluna.
    """
    conexao = sqlite3.connect(CAMINHO_BANCO_DADOS)
    conexao.row_factory = sqlite3.Row
    return conexao


def gerar_hash_senha(senha_pura: str) -> str:
    """
    Gera um hash SHA-256 criptográfico para armazenamento seguro de senhas.
    """
    return hashlib.sha256(senha_pura.encode("utf-8")).hexdigest()


def inicializar_banco_de_dados() -> None:
    """
    Cria a estrutura de tabelas no SQLite se não existirem e popula
    dados iniciais para demonstração acadêmica da equipe.
    """
    with obter_conexao() as conexao:
        cursor = conexao.cursor()

        # 1. TABELA DE CACHES DE APIs (NASA E WIKIPEDIA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caches_api (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave_cache TEXT UNIQUE NOT NULL,
                tipo_recurso TEXT NOT NULL, -- 'nasa_apod', 'nasa_busca', 'wikipedia'
                dados_json TEXT NOT NULL,
                data_criacao DATETIME NOT NULL,
                data_expiracao DATETIME NOT NULL
            );
        """)

        # 2. TABELA DE USUÁRIOS (ADMINISTRADORES, PROFESSORES E ESTUDANTES)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                papel TEXT NOT NULL DEFAULT 'ESTUDANTE', -- 'ADMINISTRADOR', 'PROFESSOR', 'ESTUDANTE'
                data_cadastro DATETIME NOT NULL
            );
        """)

        # 3. TABELA DE AUDITORIA DE LOGINS (SEGURANÇA E ACESSOS)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros_login (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                email_tentativa TEXT NOT NULL,
                data_hora DATETIME NOT NULL,
                endereco_ip TEXT,
                status TEXT NOT NULL, -- 'SUCESSO' ou 'FALHA'
                navegador TEXT,
                papel_identificado TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            );
        """)

        # 4. TABELA DE HISTÓRICO DE BUSCAS PERSONALIZADAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_buscas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                termo_pesquisado TEXT NOT NULL,
                categoria_resultado TEXT,
                total_resultados INTEGER DEFAULT 0,
                data_hora_busca DATETIME NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            );
        """)

        # Inserção de usuários padrão caso a base esteja limpa
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        if cursor.fetchone()["total"] == 0:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            senha_padrao_hash = gerar_hash_senha("espaco123")

            usuarios_padrao = [
                ("Comandante Ramon", "admin@espacoviagem.com", senha_padrao_hash, "ADMINISTRADOR", agora),
                ("Profa. Samira", "professora@espacoviagem.com", senha_padrao_hash, "PROFESSOR", agora),
                ("Emmanuel Explorador", "emmanuel@espacoviagem.com", senha_padrao_hash, "ESTUDANTE", agora),
                ("Pyerre Astrônomo", "pyerre@espacoviagem.com", senha_padrao_hash, "ESTUDANTE", agora),
            ]

            cursor.executemany("""
                INSERT INTO usuarios (nome_completo, email, senha_hash, papel, data_cadastro)
                VALUES (?, ?, ?, ?, ?)
            """, usuarios_padrao)

            # Inserção de registros de login iniciais de demonstração
            logins_iniciais = [
                (1, "admin@espacoviagem.com", (datetime.now() - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"), "127.0.0.1", "SUCESSO", "Chrome / Windows 11", "ADMINISTRADOR"),
                (2, "professora@espacoviagem.com", (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"), "192.168.0.15", "SUCESSO", "Edge / Windows", "PROFESSOR"),
                (None, "desconhecido@teste.com", (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"), "10.0.0.4", "FALHA", "Firefox / Linux", "VISITANTE"),
            ]

            cursor.executemany("""
                INSERT INTO registros_login (usuario_id, email_tentativa, data_hora, endereco_ip, status, navegador, papel_identificado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, logins_iniciais)

            # Inserção de histórico de buscas de demonstração para a professora
            buscas_iniciais = [
                (2, "Marte", "Planeta Rochoso", 12, (datetime.now() - timedelta(minutes=18)).strftime("%Y-%m-%d %H:%M:%S")),
                (2, "Buraco Negro", "Astrofísica", 25, (datetime.now() - timedelta(minutes=12)).strftime("%Y-%m-%d %H:%M:%S")),
                (2, "Telescópio James Webb", "Missão Espacial", 8, (datetime.now() - timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S")),
            ]

            cursor.executemany("""
                INSERT INTO historico_buscas (usuario_id, termo_pesquisado, categoria_resultado, total_resultados, data_hora_busca)
                VALUES (?, ?, ?, ?, ?)
            """, buscas_iniciais)

        conexao.commit()


# ====================================================================
# GERENCIAMENTO DE CACHES DE APIs (NASA E WIKIPEDIA)
# ====================================================================

def obter_cache(chave_cache: str) -> Optional[Dict[str, Any]]:
    """
    Busca um registro de cache no SQLite pela chave.
    Retorna o dicionário JSON se válido, ou None caso expirado ou inexistente.
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT dados_json, data_expiracao
                FROM caches_api
                WHERE chave_cache = ?
            """, (chave_cache,))

            registro = cursor.fetchone()
            if not registro:
                return None

            data_expiracao = datetime.strptime(registro["data_expiracao"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > data_expiracao:
                return None

            return json.loads(registro["dados_json"])
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao ler cache ({chave_cache}): {erro}")
        return None


def salvar_cache(chave_cache: str, tipo_recurso: str, dados_dict: Dict[str, Any], duracao_horas: int = 24) -> bool:
    """
    Salva ou atualiza um registro de cache no SQLite com prazo de validade.
    """
    try:
        agora = datetime.now()
        data_expiracao = agora + timedelta(hours=duracao_horas)
        dados_json = json.dumps(dados_dict, ensure_ascii=False)
        formato = "%Y-%m-%d %H:%M:%S"

        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO caches_api (chave_cache, tipo_recurso, dados_json, data_criacao, data_expiracao)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(chave_cache) DO UPDATE SET
                    dados_json = excluded.dados_json,
                    data_criacao = excluded.data_criacao,
                    data_expiracao = excluded.data_expiracao;
            """, (chave_cache, tipo_recurso, dados_json, agora.strftime(formato), data_expiracao.strftime(formato)))
            conexao.commit()
            return True
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao salvar cache ({chave_cache}): {erro}")
        return False


def limpar_todos_caches() -> int:
    """
    Exclui todos os registros de cache do SQLite (função exclusiva do Administrador).
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM caches_api")
            total = cursor.rowcount
            conexao.commit()
            return total
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao limpar caches: {erro}")
        return 0


# ====================================================================
# AUTENTICAÇÃO E CADASTRO DE USUÁRIOS
# ====================================================================

def cadastrar_usuario(nome_completo: str, email: str, senha_pura: str, papel: str = "ESTUDANTE") -> Dict[str, Any]:
    """
    Cadastra um novo usuário no banco de dados SQLite.
    Papéis aceitos: 'ADMINISTRADOR', 'PROFESSOR', 'ESTUDANTE'.
    """
    email_normalizado = email.strip().lower()
    nome_limpo = nome_completo.strip()
    papel_ajustado = papel.strip().upper()

    if papel_ajustado not in ["ADMINISTRADOR", "PROFESSOR", "ESTUDANTE"]:
        papel_ajustado = "ESTUDANTE"

    if not nome_limpo or not email_normalizado or len(senha_pura) < 4:
        return {"sucesso": False, "mensagem": "Preencha todos os campos. A senha deve ter ao menos 4 caracteres."}

    senha_hash = gerar_hash_senha(senha_pura)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nome_completo, email, senha_hash, papel, data_cadastro)
                VALUES (?, ?, ?, ?, ?)
            """, (nome_limpo, email_normalizado, senha_hash, papel_ajustado, agora))

            novo_id = cursor.lastrowid
            conexao.commit()

            return {
                "sucesso": True,
                "mensagem": f"Cadastro realizado com sucesso! Bem-vindo, {papel_ajustado.title()}.",
                "usuario": {
                    "id": novo_id,
                    "nome_completo": nome_limpo,
                    "email": email_normalizado,
                    "papel": papel_ajustado,
                    "data_cadastro": agora
                }
            }
    except sqlite3.IntegrityError:
        return {"sucesso": False, "mensagem": "Este e-mail já está cadastrado no sistema espacial."}
    except Exception as erro:
        return {"sucesso": False, "mensagem": f"Erro no cadastro: {erro}"}


def autenticar_usuario(email: str, senha_pura: str) -> Optional[Dict[str, Any]]:
    """
    Valida credenciais de login e retorna os dados do usuário autenticado.
    """
    email_normalizado = email.strip().lower()
    senha_hash = gerar_hash_senha(senha_pura)

    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome_completo, email, papel, data_cadastro
                FROM usuarios
                WHERE email = ? AND senha_hash = ?
            """, (email_normalizado, senha_hash))

            registro = cursor.fetchone()
            if registro:
                return dict(registro)
            return None
    except Exception as erro:
        print(f"[banco_de_dados] Erro na autenticação: {erro}")
        return None


# ====================================================================
# AUDITORIA DE LOGINS E ACESSOS
# ====================================================================

def registrar_log_login(email_tentativa: str, status: str, endereco_ip: str = "127.0.0.1", navegador: str = "Web Browser", usuario_id: Optional[int] = None, papel: str = "VISITANTE") -> bool:
    """
    Registra tentativa de login para fins de auditoria e segurança.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO registros_login (usuario_id, email_tentativa, data_hora, endereco_ip, status, navegador, papel_identificado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (usuario_id, email_tentativa.strip().lower(), agora, endereco_ip, status.upper(), navegador, papel.upper()))
            conexao.commit()
            return True
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao gravar log de login: {erro}")
        return False


def listar_historico_logins(limite: int = 25) -> List[Dict[str, Any]]:
    """
    Retorna os logs mais recentes de login para visualização pelo Administrador.
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT 
                    r.id, r.email_tentativa, r.data_hora, r.endereco_ip, r.status, r.navegador,
                    COALESCE(r.papel_identificado, 'VISITANTE') AS papel,
                    COALESCE(u.nome_completo, 'Visitante Não Autenticado') AS nome_usuario
                FROM registros_login r
                LEFT JOIN usuarios u ON r.usuario_id = u.id
                ORDER BY r.id DESC
                LIMIT ?
            """, (limite,))
            return [dict(linha) for linha in cursor.fetchall()]
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao listar logs de login: {erro}")
        return []


# ====================================================================
# HISTÓRICO DE BUSCAS PERSONALIZADAS (PROFESSORES E ESTUDANTES)
# ====================================================================

def salvar_busca_usuario(usuario_id: int, termo: str, categoria: str = "Astronomia", total_resultados: int = 1) -> bool:
    """
    Salva uma pesquisa realizada por um usuário logado (Professor, Estudante ou Admin).
    Nota: Visitantes anônimos não gravam nesta tabela.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    termo_limpo = termo.strip()

    if not termo_limpo or not usuario_id:
        return False

    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO historico_buscas (usuario_id, termo_pesquisado, categoria_resultado, total_resultados, data_hora_busca)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, termo_limpo, categoria, total_resultados, agora))
            conexao.commit()
            return True
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao salvar busca: {erro}")
        return False


def listar_historico_buscas_usuario(usuario_id: int, limite: int = 20) -> List[Dict[str, Any]]:
    """
    Retorna as pesquisas recentes realizadas especificamente por aquele usuário.
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, termo_pesquisado, categoria_resultado, total_resultados, data_hora_busca
                FROM historico_buscas
                WHERE usuario_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (usuario_id, limite))
            return [dict(linha) for linha in cursor.fetchall()]
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao listar buscas do usuário {usuario_id}: {erro}")
        return []


def limpar_historico_buscas_usuario(usuario_id: int) -> bool:
    """
    Limpa o histórico de pesquisas de um usuário específico.
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM historico_buscas WHERE usuario_id = ?", (usuario_id,))
            conexao.commit()
            return True
    except Exception as erro:
        print(f"[banco_de_dados] Erro ao limpar histórico: {erro}")
        return False


def obter_estatisticas_gerais() -> Dict[str, Any]:
    """
    Retorna métricas globais do sistema para o painel administrativo.
    """
    try:
        with obter_conexao() as conexao:
            cursor = conexao.cursor()

            cursor.execute("SELECT COUNT(*) AS total FROM caches_api")
            total_caches = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
            total_usuarios = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM registros_login")
            total_logins = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM historico_buscas")
            total_buscas = cursor.fetchone()["total"]

            return {
                "total_caches": total_caches,
                "total_usuarios": total_usuarios,
                "total_logins": total_logins,
                "total_buscas_salvas": total_buscas,
                "status_banco": "Online / Saudável"
            }
    except Exception as erro:
        return {
            "total_caches": 0,
            "total_usuarios": 0,
            "total_logins": 0,
            "total_buscas_salvas": 0,
            "status_banco": f"Erro: {erro}"
        }


# Inicializa o banco de dados automaticamente na inicialização
inicializar_banco_de_dados()
