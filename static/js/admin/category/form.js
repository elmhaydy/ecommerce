document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("categoryForm");
    const submitBtn = document.getElementById("submitBtn");
    const nameFrInput = document.querySelector('input[name="name_fr"]');
    const nameEnInput = document.querySelector('input[name="name_en"]');
    const slugInput = document.querySelector('input[name="slug"]');
    const generateSlugBtn = document.getElementById("generateSlugBtn");
    const deleteBtn = document.getElementById("deleteCategoryBtn");
    const deleteModal = document.getElementById("deleteModal");

    function setupCharCounter(input, counterId) {
        if (!input) return;
        const counter = document.getElementById(counterId);
        if (!counter) return;

        const updateCount = () => {
            counter.textContent = input.value.length;
        };

        input.addEventListener("input", updateCount);
        updateCount();
    }

    function generateSlug(text) {
        return text
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
    }

    function validateForm() {
        let isValid = true;

        if (nameFrInput && !nameFrInput.value.trim()) {
            nameFrInput.style.borderColor = "var(--accent-danger)";
            isValid = false;
        } else if (nameFrInput) {
            nameFrInput.style.borderColor = "";
        }

        if (slugInput && slugInput.value.includes(" ")) {
            slugInput.style.borderColor = "var(--accent-danger)";
            isValid = false;
        } else if (slugInput) {
            slugInput.style.borderColor = "";
        }

        return isValid;
    }

    setupCharCounter(nameFrInput, "nameFrCount");
    setupCharCounter(nameEnInput, "nameEnCount");

    if (generateSlugBtn && nameFrInput && slugInput) {
        generateSlugBtn.addEventListener("click", () => {
            const slug = generateSlug(nameFrInput.value);
            if (slug) slugInput.value = slug;
        });
    }

    if (slugInput) {
        slugInput.addEventListener("input", (event) => {
            event.target.value = generateSlug(event.target.value);
        });
    }

    if (form) {
        form.addEventListener("submit", (event) => {
            if (!validateForm()) {
                event.preventDefault();
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.classList.add("loading");
            }
        });
    }

    if (deleteBtn && deleteModal) {
        const modalCategoryName = document.getElementById("modalCategoryName");
        const modalProductsWarning = document.getElementById("modalProductsWarning");
        const modalProductsCount = document.getElementById("modalProductsCount");
        const deleteForm = document.getElementById("deleteForm");
        const cancelDelete = document.getElementById("cancelDelete");

        const closeDeleteModal = () => {
            deleteModal.classList.remove("show");
        };

        deleteBtn.addEventListener("click", () => {
            const categoryName = deleteBtn.dataset.name;
            const productsCount = parseInt(deleteBtn.dataset.products, 10) || 0;

            if (modalCategoryName) modalCategoryName.textContent = categoryName;
            if (deleteForm && deleteBtn.dataset.deleteUrl) {
                deleteForm.action = deleteBtn.dataset.deleteUrl;
            }

            if (modalProductsWarning && modalProductsCount) {
                if (productsCount > 0) {
                    modalProductsCount.textContent = productsCount;
                    modalProductsWarning.style.display = "flex";
                } else {
                    modalProductsWarning.style.display = "none";
                }
            }

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
