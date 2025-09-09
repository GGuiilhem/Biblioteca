/**
 * Função para formatar CPF
 * @param {string} cpf - CPF no formato 12345678901
 * @returns {string} CPF formatado (123.456.789-01)
 */
function formatarCPF(cpf) {
    if (!cpf) return '';
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

/**
 * Função para formatar telefone
 * @param {string} telefone - Telefone no formato 11987654321
 * @returns {string} Telefone formatado (11) 98765-4321
 */
function formatarTelefone(telefone) {
    if (!telefone) return '';
    
    // Remove tudo que não for número
    const numeros = telefone.replace(/\D/g, '');
    
    // Formatação para celular (11 dígitos)
    if (numeros.length === 11) {
        return numeros.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    
    // Formatação para telefone fixo (10 dígitos)
    if (numeros.length === 10) {
        return numeros.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    
    return telefone;
}

/**
 * Função para formatar data
 * @param {string} dataString - Data no formato ISO (YYYY-MM-DD)
 * @returns {string} Data formatada (DD/MM/YYYY)
 */
function formatarData(dataString) {
    if (!dataString) return '';
    
    const data = new Date(dataString);
    if (isNaN(data.getTime())) return '';
    
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    
    return `${dia}/${mes}/${ano}`;
}

/**
 * Anima os contadores de estatísticas
 */
function animateCounters() {
    const duration = 2000; // 2 segundos
    const startTime = performance.now();
    
    const updateCounter = (timestamp) => {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        document.querySelectorAll('.stat-number').forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const current = Math.floor(progress * target);
            counter.textContent = current.toLocaleString();
        });
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Garante que o valor final seja exatamente o target
            document.querySelectorAll('.stat-number').forEach(counter => {
                const target = parseInt(counter.getAttribute('data-count'));
                counter.textContent = target.toLocaleString();
            });
        }
    };
    
    requestAnimationFrame(updateCounter);
}

/**
 * Verifica se um elemento está visível na tela
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Inicialização quando o DOM estiver pronto
 */
document.addEventListener('DOMContentLoaded', function() {
    // Anima os contadores quando a seção de estatísticas estiver visível
    const statsSection = document.querySelector('.stats-section');
    let animated = false;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !animated) {
                animateCounters();
                animated = true;
            }
        });
    }, { threshold: 0.5 });
    
    if (statsSection) {
        observer.observe(statsSection);
    }
    // Formata CPFs na página
    document.querySelectorAll('[data-format-cpf]').forEach(element => {
        const cpf = element.textContent.trim();
        if (cpf) {
            element.textContent = formatarCPF(cpf);
        }
    });
    
    // Formata telefones na página
    document.querySelectorAll('[data-format-telefone]').forEach(element => {
        const telefone = element.textContent.trim();
        if (telefone) {
            element.textContent = formatarTelefone(telefone);
        }
    });
    
    // Formata datas na página
    document.querySelectorAll('[data-format-data]').forEach(element => {
        const data = element.getAttribute('data-format-data');
        if (data) {
            element.textContent = formatarData(data);
        }
    });
    
    // Adiciona confirmação para ações de exclusão
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                e.preventDefault();
            }
        });
    });
});
