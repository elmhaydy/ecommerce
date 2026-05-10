// ============================================
// ADMIN ENTITY HELPERS
// ============================================

(function () {
    function debounce(fn, wait) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => fn(...args), wait);
        };
    }

    function initFilterableTable(config) {
        const rows = Array.from(document.querySelectorAll(config.rowSelector || 'tbody tr[data-search]'));
        if (!rows.length) return;

        const searchInput = document.getElementById(config.searchInputId || 'searchInput');
        const clearSearch = document.getElementById(config.clearSearchId || 'clearSearch');
        const resetBtn = document.getElementById(config.resetBtnId || 'resetFilters');
        const prevBtn = document.getElementById(config.prevBtnId || 'prevPage');
        const nextBtn = document.getElementById(config.nextBtnId || 'nextPage');
        const startIndex = document.getElementById(config.startIndexId || 'startIndex');
        const endIndex = document.getElementById(config.endIndexId || 'endIndex');
        const totalCount = document.getElementById(config.totalCountId || 'totalCount');
        const emptyState = document.getElementById(config.emptyStateId || 'emptyState');
        const filterElements = Array.from(document.querySelectorAll(config.filterSelector || '[data-filter-key]'));
        const pageSize = config.pageSize || 10;

        let currentPage = 1;
        let filteredRows = [...rows];

        function matchesFilters(row) {
            const term = (searchInput?.value || '').trim().toLowerCase();
            const haystack = (row.dataset.search || '').toLowerCase();

            if (term && !haystack.includes(term)) {
                return false;
            }

            for (const filter of filterElements) {
                const key = filter.dataset.filterKey;
                const value = filter.value;
                if (!key || !value || value === 'all') continue;
                if ((row.dataset[key] || '') !== value) return false;
            }

            return true;
        }

        function render() {
            filteredRows = rows.filter(matchesFilters);
            const total = filteredRows.length;
            const totalPages = Math.max(1, Math.ceil(total / pageSize));
            currentPage = Math.min(currentPage, totalPages);

            rows.forEach((row) => row.classList.add('hidden-row'));

            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            filteredRows.slice(start, end).forEach((row) => row.classList.remove('hidden-row'));

            if (startIndex) startIndex.textContent = total ? String(start + 1) : '0';
            if (endIndex) endIndex.textContent = total ? String(Math.min(end, total)) : '0';
            if (totalCount) totalCount.textContent = String(total);
            if (prevBtn) prevBtn.disabled = currentPage <= 1;
            if (nextBtn) nextBtn.disabled = end >= total;
            if (emptyState) emptyState.style.display = total ? 'none' : 'block';
            if (clearSearch) clearSearch.style.display = searchInput?.value ? 'block' : 'none';
        }

        function reset() {
            if (searchInput) searchInput.value = '';
            filterElements.forEach((filter) => {
                filter.value = 'all';
            });
            currentPage = 1;
            render();
        }

        if (searchInput) {
            searchInput.addEventListener('input', debounce(() => {
                currentPage = 1;
                render();
            }, 160));
        }

        if (clearSearch) {
            clearSearch.addEventListener('click', reset);
        }

        filterElements.forEach((filter) => {
            filter.addEventListener('change', () => {
                currentPage = 1;
                render();
            });
        });

        if (resetBtn) resetBtn.addEventListener('click', reset);
        if (prevBtn) prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage -= 1;
                render();
            }
        });
        if (nextBtn) nextBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredRows.length / pageSize);
            if (currentPage < totalPages) {
                currentPage += 1;
                render();
            }
        });

        render();
        return { rows, render, reset, getFilteredRows: () => filteredRows };
    }

    function initSimpleForm(config) {
        const form = document.getElementById(config.formId);
        if (!form) return;

        const submitBtn = document.getElementById(config.submitBtnId || 'submitBtn');
        const counters = config.counters || [];

        counters.forEach((item) => {
            const field = document.querySelector(item.selector);
            const counter = document.getElementById(item.countId);
            if (!field || !counter) return;

            const update = () => {
                const count = field.value.length;
                counter.textContent = String(count);
                if (item.max && count > item.max) {
                    counter.style.color = 'var(--accent-danger)';
                } else if (item.warnAt && count >= item.warnAt) {
                    counter.style.color = 'var(--accent-warning)';
                } else {
                    counter.style.color = 'var(--text-muted)';
                }
            };

            field.addEventListener('input', update);
            update();
        });

        form.addEventListener('submit', () => {
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Enregistrement...</span>';
            }
        });
    }

    function confirmLinks(selector, messageBuilder) {
        document.querySelectorAll(selector).forEach((link) => {
            link.addEventListener('click', (event) => {
                const message = typeof messageBuilder === 'function'
                    ? messageBuilder(link)
                    : (messageBuilder || 'Confirmer cette action ?');

                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            });
        });
    }

    window.AdminEntity = {
        debounce,
        initFilterableTable,
        initSimpleForm,
        confirmLinks,
    };
})();
