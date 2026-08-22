/**
 * ====================================================================
 * SCRIPT DE AUTENTICAÇÃO E PERFIS DE USUÁRIO (SQLITE)
 * ====================================================================
 * Gerencia os formulários HTML de login e cadastro, salva o usuário
 * no localStorage para manter a sessão e atualiza dinamicamente as tabelas
 * de histórico de buscas e logs de auditoria no SQLite.
 */

document.addEventListener("DOMContentLoaded", function () {
    const formCadastro = document.getElementById("form-cadastro-html");
    const formLogin = document.getElementById("form-login-html");
    const containerHistoricoBuscas = document.getElementById("corpo-tabela-buscas");
    const containerLogsAuditoria = document.getElementById("corpo-tabela-logins");
    const btnLimparHistorico = document.getElementById("btn-limpar-historico");
    const btnLimparCaches = document.getElementById("btn-limpar-caches-admin");

    // Atualiza os badges do cabeçalho com base no usuário logado
    atualizarInterfacePerfil();

    // 1. Processamento do Formulário de Cadastro
    if (formCadastro) {
        formCadastro.addEventListener("submit", async function (evento) {
            evento.preventDefault();
            const dados = new FormData(formCadastro);
            const alerta = document.getElementById("alerta-cadastro");

            try {
                const resposta = await fetch("/api/cadastrar", {
                    method: "POST",
                    body: dados
                });
                const resultado = await resposta.json();

                if (alerta) {
                    alerta.style.display = "block";
                    alerta.innerText = resultado.mensagem;
                    alerta.style.color = resultado.sucesso ? "#34d399" : "#f87171";
                }

                if (resultado.sucesso) {
                    formCadastro.reset();
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 1500);
                }
            } catch (erro) {
                console.error("Erro ao cadastrar:", erro);
            }
        });
    }

    // 2. Processamento do Formulário de Login
    if (formLogin) {
        formLogin.addEventListener("submit", async function (evento) {
            evento.preventDefault();
            const dados = new FormData(formLogin);
            const alerta = document.getElementById("alerta-login");

            try {
                const resposta = await fetch("/api/login", {
                    method: "POST",
                    body: dados
                });
                const resultado = await resposta.json();

                if (alerta) {
                    alerta.style.display = "block";
                    alerta.innerText = resultado.mensagem;
                    alerta.style.color = resultado.sucesso ? "#34d399" : "#f87171";
                }

                if (resultado.sucesso) {
                    // Salva a sessão no localStorage
                    localStorage.setItem("usuario_espacial", JSON.stringify(resultado.usuario));
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } catch (erro) {
                console.error("Erro ao fazer login:", erro);
            }
        });
    }

    // 3. Botão de Logout
    const btnLogout = document.getElementById("btn-fazer-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", function () {
            localStorage.removeItem("usuario_espacial");
            window.location.href = "/";
        });
    }

    // 4. Limpeza de Histórico de Buscas
    if (btnLimparHistorico) {
        btnLimparHistorico.addEventListener("click", async function () {
            const usuarioAtivo = JSON.parse(localStorage.getItem("usuario_espacial") || "null");
            if (!usuarioAtivo) return;

            if (confirm("Deseja realmente limpar todo o seu histórico de pesquisas?")) {
                const resp = await fetch(`/api/usuario/historico?usuario_id=${usuarioAtivo.id}`, { method: "DELETE" });
                const res = await resp.json();
                if (res.sucesso) {
                    if (containerHistoricoBuscas) {
                        containerHistoricoBuscas.innerHTML = "<tr><td colspan='3' style='text-align:center; color:#64748b;'>Nenhuma busca salva no histórico.</td></tr>";
                    }
                }
            }
        });
    }

    // 5. Limpeza de Caches pelo Administrador
    if (btnLimparCaches) {
        btnLimparCaches.addEventListener("click", async function () {
            if (confirm("Deseja limpar todos os caches da NASA e Wikipedia armazenados no SQLite?")) {
                const resp = await fetch("/api/caches/limpar", { method: "POST" });
                const res = await resp.json();
                alert(res.mensagem);
                window.location.reload();
            }
        });
    }

    function atualizarInterfacePerfil() {
        const usuarioAtivo = JSON.parse(localStorage.getItem("usuario_espacial") || "null");
        const elementoBadge = document.getElementById("badge-perfil-cabecalho");

        if (elementoBadge) {
            if (usuarioAtivo) {
                let icone = "🚀";
                if (usuarioAtivo.papel === "ADMINISTRADOR") icone = "👑";
                if (usuarioAtivo.papel === "PROFESSOR") icone = "🎓";

                elementoBadge.innerHTML = `${icone} ${usuarioAtivo.nome_completo} (${usuarioAtivo.papel})`;
            } else {
                elementoBadge.innerHTML = "🔭 Visitante (Sem Login)";
            }
        }
    }
});
