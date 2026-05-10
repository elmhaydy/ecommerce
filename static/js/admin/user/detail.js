document.addEventListener('DOMContentLoaded', () => {
    const highlightCards = document.querySelectorAll('.snippet-card');
    highlightCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 40}ms`;
    });
});
