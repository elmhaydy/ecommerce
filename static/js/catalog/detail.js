document.addEventListener("DOMContentLoaded", () => {
  const mainImage = document.getElementById("mainProductImage");
  const thumbs = document.querySelectorAll(".thumb");
  const addCartForm = document.getElementById("addCartForm");
  const qtyHiddenInput = document.getElementById("qtyHiddenInput");

  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      const img = thumb.dataset.img;

      if (mainImage && img) {
        mainImage.src = img;
      }

      thumbs.forEach((item) => item.classList.remove("active"));
      thumb.classList.add("active");
    });
  });

  const qtyInput = document.getElementById("qtyInput");
  const qtyButtons = document.querySelectorAll(".qty-btn");

  qtyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (!qtyInput) return;

      let value = parseInt(qtyInput.value || "1");
      const max = parseInt(qtyInput.getAttribute("max") || "99");

      if (button.dataset.action === "plus" && value < max) {
        value++;
      }

      if (button.dataset.action === "minus" && value > 1) {
        value--;
      }

      qtyInput.value = value;
      if (qtyHiddenInput) {
        qtyHiddenInput.value = String(value);
      }
    });
  });

  if (qtyInput && qtyHiddenInput) {
    qtyInput.addEventListener("input", () => {
      let value = parseInt(qtyInput.value || "1", 10);
      const max = parseInt(qtyInput.getAttribute("max") || "99", 10);

      if (Number.isNaN(value) || value < 1) value = 1;
      if (value > max) value = max;

      qtyInput.value = String(value);
      qtyHiddenInput.value = String(value);
    });
  }

  if (addCartForm) {
    addCartForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const submitButton = addCartForm.querySelector(".add-cart-btn");
      const formData = new FormData(addCartForm);

      try {
        if (submitButton) {
          submitButton.disabled = true;
        }

        const response = await fetch(addCartForm.action, {
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
  }

  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.tab;

      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabPanels.forEach((panel) => panel.classList.remove("active"));

      button.classList.add("active");
      document.getElementById(target)?.classList.add("active");
    });
  });
});
