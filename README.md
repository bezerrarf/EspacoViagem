# 🚀 Espaço Viagem

Bem-vindo ao **Espaço Viagem**! Um ambiente educacional interativo desenvolvido para estudantes e entusiastas de astronomia. Nosso objetivo é descomplicar a ciência espacial unindo imagens em alta definição e dados curiosos sobre o nosso sistema solar de forma rápida e acessível.

Projeto desenvolvido em equipe por: **Ramon, Samira, Emmanuel e Pyerre** para estudos práticos de arquitetura de software, programação web e astronomia.

---

## 🎯 O Projeto

Este projeto foi construído focando na performance, estrutura limpa e responsividade. Através dele, conectamos os usuários ao cosmos utilizando uma interface moderna e um sistema de leitura de dados leve, simulando o consumo de um banco de dados real através da arquitetura MVC (Model-View-Controller). 

**Público-alvo:** Estudantes de Astronomia e amantes do universo de todas as idades.

---

## ✨ Funcionalidades Principais

* 🌌 **Exploração Planetária (Carrossel Automático):** Uma vitrine horizontal que exibe astros do nosso sistema solar (incluindo o Sol, planetas e cometas famosos). O carrossel desliza suavemente de forma automática a cada 10 segundos, graças a um motor JavaScript embutido.
* 📱 **Design 100% Responsivo:** O layout se adapta perfeitamente a qualquer tamanho de tela, desde monitores ultrawide até smartphones pequenos, garantindo uma navegação sem rolagem horizontal indesejada.
* 🌙 **Tema Escuro Espacial (Dark Mode):** Interface imersiva que protege a visão do usuário e destaca o brilho e as cores reais das fotografias espaciais.
* 📄 **Motor de Dados Dinâmico:** Os dados não estão presos (hardcoded) no visual. A aplicação lê dinamicamente as informações, massas e distâncias dos planetas diretamente de um arquivo de texto, montando os cartões de forma automática.

---

## 🛠️ Tecnologias Utilizadas

* **Backend / Lógica:** Python 3 e FastHTML (Starlette/Uvicorn)
* **Frontend Estrutural:** Componentes HTML gerados via Python
* **Frontend Visual:** CSS3 Puro (Flexbox, Media Queries e CSS Reset)
* **Automação de UI:** JavaScript Vanilla (Puro) injetado via Controller
* **Ambiente de Desenvolvimento:** GitHub Codespaces (Cloud)
* **Gerenciador de Pacotes:** `uv`

---

## 📂 Estrutura do Projeto (Arquitetura MVC)

Para manter o código organizado, escalável e facilitar o trabalho da equipe, adotamos fielmente o padrão **MVC (Model-View-Controller)**.

```text
EspacoViagem/
│
├── controllers/      # (CONTROLLER) Regras de Negócio e Rotas
│   └── main.py       # Ponto de entrada: configura o FastHTML, resolve rotas, injeta CSS/JS e liga as Views aos Models.
│
├── models/           # (MODEL) Lógica de Dados
│   └── astros.txt    # Banco de dados local contendo nome, distância, massa, curiosidade e link da imagem de cada astro.
│
├── views/            # (VIEW) Interface do Usuário
│   ├── static/       
│   │   └── style.css # Folha de estilos garantindo o visual e a responsividade (Media Queries).
│   └── home.py       # Gera dinamicamente a estrutura HTML lendo os dados de 'models'.
│
└── README.md         # Documentação atual do projeto
