document.addEventListener("DOMContentLoaded", () => {
  const cartItems = document.querySelectorAll(".cart-item");
  const suggestionsTrack = document.getElementById("suggestionsTrack");
  const suggestionsPrev = document.getElementById("suggestionsPrev");
  const suggestionsNext = document.getElementById("suggestionsNext");

  cartItems.forEach((item) => {
    item.addEventListener("mouseenter", () => {
      item.style.transform = "translateY(-2px)";
      item.style.transition = "0.25s ease";
    });

    item.addEventListener("mouseleave", () => {
      item.style.transform = "translateY(0)";
    });
  });

  if (suggestionsTrack && suggestionsPrev && suggestionsNext) {
    const suggestionCards = Array.from(suggestionsTrack.querySelectorAll(".suggestion-card"));
    let suggestionIndex = 0;
    let visibleCards = 4;

    const getVisibleCards = () => {
      if (window.innerWidth <= 650) return 1;
      if (window.innerWidth <= 1100) return 2;
      return 4;
    };

    const syncSuggestionsTrack = () => {
      visibleCards = getVisibleCards();
      const maxIndex = Math.max(suggestionCards.length - visibleCards, 0);
      suggestionIndex = Math.min(suggestionIndex, maxIndex);

      const cardWidth = suggestionCards[0]?.getBoundingClientRect().width || 0;
      const trackStyle = window.getComputedStyle(suggestionsTrack);
      const gap = parseFloat(trackStyle.columnGap || trackStyle.gap || "0");
      const offset = (cardWidth + gap) * suggestionIndex;

      suggestionsTrack.style.transform = `translateX(-${offset}px)`;
      suggestionsPrev.disabled = suggestionIndex <= 0;
      suggestionsNext.disabled = suggestionIndex >= maxIndex;
    };

    suggestionsPrev.addEventListener("click", () => {
      suggestionIndex = Math.max(suggestionIndex - 1, 0);
      syncSuggestionsTrack();
    });

    suggestionsNext.addEventListener("click", () => {
      const maxIndex = Math.max(suggestionCards.length - visibleCards, 0);
      suggestionIndex = Math.min(suggestionIndex + 1, maxIndex);
      syncSuggestionsTrack();
    });

    window.addEventListener("resize", syncSuggestionsTrack);
    syncSuggestionsTrack();
  }
});
