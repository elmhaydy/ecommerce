document.addEventListener("DOMContentLoaded", () => {
  const filterForm = document.getElementById("filterForm");
  const checkboxes = document.querySelectorAll(".shop-sidebar input[type='checkbox']");
  const cards = document.querySelectorAll(".product-card");
  const addToCartForms = document.querySelectorAll(".product-action-form");

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (filterForm) {
        filterForm.submit();
      }
    });
  });

  cards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.classList.add("is-hovered");
    });

    card.addEventListener("mouseleave", () => {
      card.classList.remove("is-hovered");
    });
  });

  addToCartForms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const submitButton = form.querySelector(".action-cart");
      const formData = new FormData(form);

      try {
        if (submitButton) {
          submitButton.disabled = true;
        }

        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest"
          }
        });

        const payload = await response.json();

        if (!response.ok || !payload.success) {
          throw new Error(payload.message || "Impossible d'ajouter ce produit au panier.");
        }

        if (typeof window.renderCartDrawer === "function" && payload.cart) {
          window.renderCartDrawer(payload.cart);
        }

        if (typeof window.openCartDrawer === "function") {
          window.openCartDrawer();
        }
      } catch (error) {
        window.alert(error.message || "Impossible d'ajouter ce produit au panier.");
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
        }
      }
    });
  });
});
