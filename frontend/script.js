async function carregarDados() {
try {
    const response = await fetch('../requests.json');
    const dados = await response.json();

    if (!Array.isArray(dados) || dados.length === 0) {
        document.body.innerHTML = '<div class="alert alert-warning text-center mt-5">Nenhum dado disponível.</div>';
        return;
    }

    // Função auxiliar para converter "1.234,56" -> 1234.56
    const parseNumber = (valor) => {
        if (typeof valor !== "string") return 0;
        return parseFloat(valor.replace(/\./g, "").replace(",", "."));
    };

    // Pega as chaves do primeiro objeto
    const colunas = Object.keys(dados[0]);

    // Monta a tabela
    const header = document.getElementById('tabela-header');
    const body = document.getElementById('tabela-body');

    header.innerHTML = colunas.map(c => `<th>${c}</th>`).join('');
    body.innerHTML = dados.map(linha =>
        `<tr>${colunas.map(c => `<td>${linha[c]}</td>`).join('')}</tr>`
    ).join('');

    // Dados para os gráficos
    const projetos = dados.map((d) => d["Def.projeto"]);
    const valoresTotais = dados.map((d) =>
        parseNumber(d["Valor total em reais"])
    );
    const valSuj = dados.map((d) => parseNumber(d["Val suj cont loc R$"]));
    const valCont = dados.map((d) => parseNumber(d["Valor cont local R$"]));

    // Paleta de cores
    const cores = projetos.map((_, i) =>
      `hsl(${i * 50 % 360}, 70%, 60%)`
    );

    // Gráfico de Colunas
    new Chart(document.getElementById('chartColunas'), {
        type: 'bar',
        data: {
        labels: projetos,
        datasets: [{
            label: 'Valor total em reais (R$)',
            data: valoresTotais,
            backgroundColor: cores,
            borderRadius: 8
        }]
        },
        options: {
        responsive: true,
        scales: {
            y: {
            beginAtZero: true,
            ticks: {
                callback: v => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
            }
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
            callbacks: {
                label: ctx => ctx.raw.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
            }
            }
        }
        }
    });

    // Gráfico de Pizza
    const totalValSuj = valSuj.reduce((a, b) => a + b, 0);
    const totalValCont = valCont.reduce((a, b) => a + b, 0);
    
    new Chart(document.getElementById("chartPizza"), {
        type: "pie",
        data: {
        labels: ["Val suj cont loc R$", "Valor cont local R$"],
        datasets: [
            {
            data: [totalValSuj, totalValCont],
            backgroundColor: ["#36A2EB", "#FF6384"],
            },
        ],
        },
        options: {
        responsive: true,
        plugins: {
            legend: { position: "bottom" },
            tooltip: {
            callbacks: {
                label: (ctx) =>
                `${ctx.label}: ${ctx.raw.toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                })}`,
            },
            },
        },
        },
    });
    } catch (error) {
    console.error("Erro ao carregar JSON:", error);
    document.body.innerHTML =
        '<div class="alert alert-danger text-center mt-5">Erro ao carregar os dados.</div>';
    }
}

carregarDados();