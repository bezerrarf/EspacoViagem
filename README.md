# 🚀 Espaço Viagem — Exploração Cósmica Interativa

> **Ambiente educacional de astronomia com integração oficial das APIs da NASA e da Wikipedia, persistência em Banco de Dados SQLite, controle de perfis de acesso e interface moderna em HTML5, CSS3 e JavaScript.**

Projeto desenvolvido em equipe por: **Ramon, Samira, Emmanuel e Pyerre** para estudos práticos de Arquitetura de Software (MVC), Programação Web, Banco de Dados e Ciência Espacial.

---

## ✨ Funcionalidades Principais

1. 🔍 **Busca Cósmica Centralizada (NASA + Wikipedia)**:
   - Barra de pesquisa no centro da tela para pesquisar planetas, estrelas, luas, asteroides, buracos negros e galáxias.
   - Retorno conjunto de **fotografias oficiais da NASA** e **resumos científicos em português da Wikipedia**.
2. 🔭 **Imagem Astronômica do Dia (APOD)**:
   - Exibição diária da fotografia em alta definição da NASA acompanhada de contextualização científica.
3. 💾 **Banco de Dados SQLite Persistente (`models/espaco_viagem.db`)**:
   - **Tabela de Caches**: Evita sobrecarga de requisições armazenando respostas da NASA e Wikipedia.
   - **Tabela de Usuários**: Cadastro de exploradores com controle de senhas criptografadas em SHA-256.
   - **Tabela de Auditoria de Logins**: Registro detalhado de acessos (IP, data/hora, status e navegador).
   - **Tabela de Histórico de Buscas**: Armazena as pesquisas personalizadas de professores e estudantes.
4. 👥 **Perfis e Níveis de Acesso (RBAC)**:
   - 👑 **Administrador**: Gestão da base, auditoria de todos os logins e limpeza de caches.
   - 🎓 **Professor / Educador**: Acesso a resumos didáticos e histórico de pesquisas salvo no SQLite.
   - 🚀 **Visitante (Sem Login)**: Navegação e busca anônima livre **sem gravação de histórico**.
5. 🌌 **Front-End Cósmico & Rolagem Vertical Fluida**:
   - Layout longo e dinâmico com rolagem vertical livre.
   - Fundo espacial em movimento contínuo (*loop cósmico animado via CSS*).
   - Carrossel planetário suave com autoplay de 6s, setas de navegação e pausa ao passar o mouse.
   - Local reservado para inserção de nova logomarca (`views/static/imagens/logo.png`).

---

## 🏛️ Arquitetura do Projeto (Padrão MVC)

```text
EspacoViagem-Visual/
│
├── .env                             # Chaves de API (NASA_API_KEY, URLs Wikipedia, Porta)
├── .gitignore                       # Configuração para o repositório GitHub
├── iniciar_servidor.bat             # Atalho executável para iniciar no Windows
├── pyproject.toml                   # Dependências do Python
├── README.md                        # Documentação completa
│
├── controllers/                     # [CONTROLLER - Orquestração de Rotas e APIs]
│   ├── __init__.py
│   └── main.py                      # Ponto de entrada, entrega de páginas HTML e endpoints JSON
│
├── models/                          # [MODEL - Banco de Dados, Caches e APIs Externas]
│   ├── __init__.py
│   ├── banco_de_dados.py            # SQLite: Tabelas de caches, usuarios, registros_login e historico_buscas
│   ├── nasa_api.py                  # Integração oficial com a API da NASA (APOD, NeoWs, Imagens)
│   ├── wikipedia_api.py             # Integração com a API da Wikipedia em português
│   ├── repositorio_astros.py        # Leitor e formatador dos dados de astros
│   ├── astros.txt                   # Base de dados textual de astros com categorias e medidas
│   └── espaco_viagem.db             # Arquivo binário gerado pelo SQLite
│
├── views/                           # [VIEW - Front-End em HTML5 Puro]
│   ├── index.html                   # Tela Inicial: Rolagem Vertical, Busca Central e APOD + Wikipedia
│   ├── cadastro.html                # Formulário HTML de Cadastro (Admin, Professor, Estudante)
│   ├── login.html                   # Formulário HTML de Login e Painel com Histórico de Buscas
│   ├── planetas.html                # Galeria de Planetas com Filtros e Resumos da Wikipedia
│   ├── sobre.html                   # Apresentação da Equipe e Arquitetura MVC
│   │
│   └── static/                      # Recursos Estáticos
│       ├── css/style.css            # Estilos cósmicos, fundo animado em loop e responsividade
│       ├── js/busca_cosmica.js      # Lógica JS da busca centralizada (NASA + Wikipedia)
│       ├── js/carrossel.js          # Lógica JS do carrossel suave com botões e pausa no hover
│       ├── js/autenticacao.js       # Validações dos formulários de cadastro e login
│       └── imagens/logo_padrao.svg  # Logo vetorial espacial
```

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12+, FastHTML / Starlette, Uvicorn
- **Banco de Dados:** SQLite3 (nativo do Python, sem dependências pesadas)
- **Frontend Estrutural:** HTML5 Semântico Puro
- **Frontend Visual:** CSS3 Puro (Glassmorphism, Flexbox, Grid, Animação em Loop)
- **Frontend Interativo:** JavaScript Vanilla (Fetch API, DOM Events)
- **APIs Externas:** NASA Open APIs (APOD, NeoWs, Images) & Wikipedia REST API (pt)

---

### 🚀 Executando o Projeto

### Pré-requisitos
Python 3.12 ou superior e o gerenciador de pacotes [uv](https://docs.astral.sh/uv/) instalado.

### Instalação do uv

```bash
# Linux / macOS / GitHub Codespaces
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Executando o servidor

```bash
# Na pasta raiz do projeto
uv run python controllers/main.py

# O servidor sobe por padrão em:
# http://localhost:5001
```

### Executando via Docker

```bash
docker build -t espaco-viagem .
docker run -p 5001:5001 --env-file .env espaco-viagem
```

> ⚠️ Antes de rodar, crie um arquivo `.env` na raiz do projeto com as variáveis necessárias (`NASA_API_KEY`, URLs e `PORTA`). Ele não vem do repositório — veja o `.env.example` (se houver) ou a documentação técnica completa.

---

## 👥 Integrantes da Equipe

- 👨‍💻 **Ramon** — Liderança Técnica, Backend e Arquitetura MVC
- 👩‍💻 **Samira** — Front-End, Design System Cósmico, UI/UX e Responsividade
- 👨‍🚀 **Emmanuel** — Integração com APIs da NASA e Wikipedia
- 👨‍🔬 **Pyerre** — Modelagem do Banco SQLite, Caches e Segurança
