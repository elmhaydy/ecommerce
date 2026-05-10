document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("productForm");
    const submitBtn = document.getElementById("submitBtn");
    const stockInput = document.querySelector('input[name="stock"]');
    const lowStockInput = document.querySelector('input[name="low_stock_threshold"]');
    const priceInput = document.querySelector('input[name="price"]');
    const oldPriceInput = document.querySelector('input[name="old_price"]');
    const slugInput = document.querySelector('input[name="slug"]');
    const nameFrInput = document.querySelector('input[name="name_fr"]');
    const descriptionFr = document.querySelector('textarea[name="description_fr"]');
    const descriptionEn = document.querySelector('textarea[name="description_en"]');

    function updateCharCount(textarea, counterId) {
        if (!textarea) return;
        const counter = document.getElementById(counterId);
        if (!counter) return;
        counter.textContent = textarea.value.length;
    }

    function generateSlug(value) {
        return value
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
    }

    function updateStockIndicator() {
        const stock = parseInt(stockInput?.value, 10) || 0;
        const threshold = parseInt(lowStockInput?.value, 10) || 5;
        const stockStatusText = document.getElementById("stockStatusText");
        const stockProgressBar = document.getElementById("stockProgressBar");

        if (!stockStatusText || !stockProgressBar) return;

        if (stock === 0) {
            stockStatusText.textContent = "Rupture de stock";
            stockStatusText.style.color = "var(--accent-danger)";
            stockProgressBar.style.width = "0%";
            stockProgressBar.style.background = "var(--accent-danger)";
        } else if (stock <= threshold) {
            stockStatusText.textContent = "Stock faible";
            stockStatusText.style.color = "var(--accent-warning)";
            stockProgressBar.style.width = `${Math.min((stock / Math.max(threshold, 1)) * 100, 100)}%`;
            stockProgressBar.style.background = "var(--accent-warning)";
        } else {
            stockStatusText.textContent = "Stock disponible";
            stockStatusText.style.color = "var(--accent-success)";
            stockProgressBar.style.width = `${Math.min(stock, 100)}%`;
            stockProgressBar.style.background = "var(--gradient-primary)";
        }
    }

    function validatePrices() {
        const price = parseFloat(priceInput?.value) || 0;
        const oldPrice = parseFloat(oldPriceInput?.value) || 0;

        if (oldPriceInput) {
            oldPriceInput.style.borderColor = oldPrice > 0 && oldPrice <= price ? "var(--accent-warning)" : "";
        }
    }

    if (descriptionFr) {
        updateCharCount(descriptionFr, "descFrCount");
        descriptionFr.addEventListener("input", () => updateCharCount(descriptionFr, "descFrCount"));
    }

    if (descriptionEn) {
        updateCharCount(descriptionEn, "descEnCount");
        descriptionEn.addEventListener("input", () => updateCharCount(descriptionEn, "descEnCount"));
    }

    if (stockInput) {
        stockInput.addEventListener("input", updateStockIndicator);
        updateStockIndicator();
    }

    if (lowStockInput) {
        lowStockInput.addEventListener("input", updateStockIndicator);
    }

    if (priceInput && oldPriceInput) {
        priceInput.addEventListener("input", validatePrices);
        oldPriceInput.addEventListener("input", validatePrices);
    }

    if (nameFrInput && slugInput) {
        nameFrInput.addEventListener("blur", () => {
            if (!slugInput.value.trim()) {
                slugInput.value = generateSlug(nameFrInput.value);
            }
        });

        slugInput.addEventListener("input", (event) => {
            event.target.value = generateSlug(event.target.value);
        });
    }

    if (form) {
        form.addEventListener("submit", (event) => {
            const price = parseFloat(priceInput?.value) || 0;
            const stock = parseInt(stockInput?.value, 10) || 0;

            if (!nameFrInput?.value.trim() || !descriptionFr?.value.trim() || price <= 0 || stock < 0) {
                event.preventDefault();
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add("loading");
            }
        });
    }

    const deleteBtn = document.getElementById("deleteProductBtn");
    const deleteModal = document.getElementById("deleteProductModal");

    if (deleteBtn && deleteModal) {
        const modalName = document.getElementById("modalProductName");
        const cancelDelete = document.getElementById("cancelDeleteModal");

        const closeDeleteModal = () => {
            deleteModal.classList.remove("show");
        };

        deleteBtn.addEventListener("click", () => {
            if (modalName) modalName.textContent = deleteBtn.dataset.name;
            deleteModal.classList.add("show");
        });

        if (cancelDelete) {
            cancelDelete.addEventListener("click", closeDeleteModal);
        }

        deleteModal.addEventListener("click", (event) => {
            if (event.target === deleteModal) {
                closeDeleteModal();
            }
        });
    }
});
