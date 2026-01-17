function selecionarTamanho(elemento, produtoId) {
    // 1. Seleciona todos os botões APENAS deste produto
    const botoes = document.querySelectorAll('.btn-tamanho-' + produtoId);
    
    // 2. Reseta o estilo de todos os botões do grupo
    botoes.forEach(btn => {
        btn.classList.remove('btn-dark');
        btn.classList.add('btn-outline-dark');
        btn.style.backgroundColor = "transparent";
        btn.style.color = "black";
    });

    // 3. Aplica o estilo de selecionado no botão clicado
    elemento.classList.remove('btn-outline-dark');
    elemento.classList.add('btn-dark');
    elemento.style.backgroundColor = "black";
    elemento.style.color = "white";

    // 4. Salva o valor no input oculto específico deste produto
    const tamanho = elemento.getAttribute('data-tamanho');
    const inputOculto = document.getElementById('tamanho_escolhido_' + produtoId);
    
    if (inputOculto) {
        inputOculto.value = tamanho;
        console.log("Produto " + produtoId + " - Tamanho selecionado: " + tamanho);
    }
}

function adicionarComTamanho(produtoId) {
    const input = document.getElementById('tamanho_escolhido_' + produtoId);
    const tamanho = input ? input.value : "";

    if (!tamanho || tamanho === "") {
        alert("Por favor, selecione um tamanho antes de adicionar ao carrinho!");
        return;
    }

    // Redireciona para a sua view do Django
    window.location.href = "/carrinho/add/" + produtoId + "/?tamanho=" + tamanho;
}

function scrollSlider(direction) {
    const row = document.getElementById('destaqueRow');
    const scrollAmount = row.clientWidth * 0.8; // Rola 80% da tela visível
    if(direction === 'left') {
        row.scrollLeft -= scrollAmount;
    } else {
        row.scrollLeft += scrollAmount;
    }
}