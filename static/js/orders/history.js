document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".orders-tab");
  const cards = document.querySelectorAll("[data-order-card]");
  const results = document.getElementById("ordersResults");
  const emptyState = document.getElementById("ordersFilteredEmpty");

  if (!tabs.length || !cards.length) {
    return;
  }

  const applyFilter = (filter) => {
    let visibleCount = 0;

    cards.forEach((card) => {
      const group = card.dataset.group;
      const shouldShow = filter === "all" || group === filter;
      card.hidden = !shouldShow;
      if (shouldShow) {
        visibleCount += 1;
      }
    });

    if (results) {
      results.hidden = visibleCount === 0;
    }

    if (emptyState) {
      emptyState.classList.toggle("is-hidden", visibleCount > 0);
    }
  };

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      applyFilter(tab.dataset.filter || "all");
    });
  });
});
