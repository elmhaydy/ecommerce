// ============================================
// CATEGORY MANAGEMENT - MODERN INTERACTIONS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    const statusFilter = document.getElementById('statusFilter');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const categoriesGrid = document.getElementById('categoriesGrid');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const startIndexSpan = document.getElementById('startIndex');
    const endIndexSpan = document.getElementById('endIndex');
    const totalCountSpan = document.getElementById('totalCount');
    
    // Variables
    let currentPage = 1;
    let itemsPerPage = 12;
    let filteredCategories = [];
    let allCategories = [];
    
    // Parse categories from DOM
    function parseCategories() {
        const cards = document.querySelectorAll('.category-card');
        allCategories = [];
        
        cards.forEach(card => {
            const category = {
                id: card.dataset.categoryId,
                name: card.dataset.name,
                nameDisplay: card.querySelector('.category-name')?.textContent || '',
                status: card.dataset.status === 'true',
                products: parseInt(card.dataset.products) || 0,
                element: card
            };
            allCategories.push(category);
        });
        
        filteredCategories = [...allCategories];
        updateStatistics();
        updateFilteredCount();
        renderCurrentPage();
    }
    
    // Update statistics
    function updateStatistics() {
        const activeCount = allCategories.filter(c => c.status).length;
        const totalProducts = allCategories.reduce((sum, c) => sum + c.products, 0);
        const avgProducts = allCategories.length > 0 ? (totalProducts / allCategories.length).toFixed(1) : 0;
        
        const activeCountElem = document.getElementById('activeCount');
        const totalProductsElem = document.getElementById('totalProducts');
        const avgProductsElem = document.getElementById('avgProducts');
        
        if (activeCountElem) activeCountElem.textContent = activeCount;
        if (totalProductsElem) totalProductsElem.textContent = totalProducts;
        if (avgProductsElem) avgProductsElem.textContent = avgProducts;
    }
    
    // Filter categories
    function filterCategories() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const statusValue = statusFilter.value;
        
        filteredCategories = allCategories.filter(category => {
            // Search filter
            if (searchTerm && !category.name.includes(searchTerm)) {
                return false;
            }
            
            // Status filter
            if (statusValue !== 'all') {
                const isActive = statusValue === 'active';
                if (category.status !== isActive) return false;
            }
            
            return true;
        });
        
        updateFilteredCount();
        currentPage = 1;
        renderCurrentPage();
        
        // Show/hide clear search button
        clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
    }
    
    // Update filter count display
    function updateFilteredCount() {
        const totalCount = filteredCategories.length;
        if (totalCountSpan) totalCountSpan.textContent = totalCount;
        
        if (totalCount === 0 && categoriesGrid) {
            showEmptyFilterState();
        } else {
            hideEmptyFilterState();
        }
    }
    
    // Show empty filter state
    function showEmptyFilterState() {
        let emptyMsg = document.querySelector('.empty-filter-state');
        if (!emptyMsg && categoriesGrid) {
            emptyMsg = document.createElement('div');
            emptyMsg.className = 'empty-state empty-filter-state';
            emptyMsg.innerHTML = `
                <i class="fas fa-search"></i>
                <h3>Aucun résultat</h3>
                <p>Aucune catégorie ne correspond à vos critères</p>
                <button class="btn-reset" onclick="resetFilters()">
                    <i class="fas fa-undo-alt"></i> Réinitialiser les filtres
                </button>
            `;
            categoriesGrid.appendChild(emptyMsg);
        }
        
        // Hide all category cards
        allCategories.forEach(category => {
            category.element.style.display = 'none';
        });
    }
    
    function hideEmptyFilterState() {
        const emptyMsg = document.querySelector('.empty-filter-state');
        if (emptyMsg) emptyMsg.remove();
    }
    
    // Render current page
    function renderCurrentPage() {
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageCategories = filteredCategories.slice(start, end);
        
        // Hide all categories first
        allCategories.forEach(category => {
            category.element.style.display = 'none';
        });
        
        // Show page categories
        pageCategories.forEach(category => {
            category.element.style.display = '';
        });
        
        // Update pagination info
        if (startIndexSpan) startIndexSpan.textContent = filteredCategories.length > 0 ? start + 1 : 0;
        if (endIndexSpan) endIndexSpan.textContent = Math.min(end, filteredCategories.length);
        
        // Update pagination buttons
        if (prevPageBtn) prevPageBtn.disabled = currentPage === 1;
        if (nextPageBtn) nextPageBtn.disabled = end >= filteredCategories.length;
    }
    
    // Reset filters
    function resetFilters() {
        if (searchInput) searchInput.value = '';
        if (statusFilter) statusFilter.value = 'all';
        if (clearSearchBtn) clearSearchBtn.style.display = 'none';
        filterCategories();
    }
    
    // Delete modal
    function showDeleteModal(categoryId, categoryName, productsCount, deleteUrl) {
        const modal = document.getElementById('deleteModal');
        const deleteCategoryName = document.getElementById('deleteCategoryName');
        const deleteForm = document.getElementById('deleteForm');
        const productsWarning = document.getElementById('productsWarning');
        const productsCountSpan = document.getElementById('productsCount');
        
        deleteCategoryName.textContent = categoryName;
        deleteForm.action = deleteUrl;
        
        if (productsCount > 0) {
            productsCountSpan.textContent = productsCount;
            productsWarning.style.display = 'flex';
        } else {
            productsWarning.style.display = 'none';
        }
        
        modal.classList.add('show');
        
        // Handle cancel
        const cancelBtn = document.getElementById('cancelDelete');
        const closeModal = () => {
            modal.classList.remove('show');
            cancelBtn.removeEventListener('click', closeModal);
        };
        
        cancelBtn.addEventListener('click', closeModal);
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Attach delete event listeners
    function attachDeleteListeners() {
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.removeEventListener('click', deleteHandler);
            btn.addEventListener('click', deleteHandler);
        });
    }
    
    function deleteHandler(e) {
        e.preventDefault();
        const categoryId = this.dataset.id;
        const categoryName = this.dataset.name;
        const productsCount = parseInt(this.dataset.products) || 0;
        const deleteUrl = this.dataset.deleteUrl;
        showDeleteModal(categoryId, categoryName, productsCount, deleteUrl);
    }
    
    // Debounce utility
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Highlight new category (from URL param)
    function checkForHighlights() {
        const urlParams = new URLSearchParams(window.location.search);
        const highlightId = urlParams.get('highlight');
        if (highlightId) {
            const card = document.querySelector(`.category-card[data-category-id="${highlightId}"]`);
            if (card) {
                card.classList.add('highlight');
                setTimeout(() => {
                    card.classList.remove('highlight');
                }, 2000);
                
                // Remove from URL
                const newUrl = window.location.pathname;
                window.history.replaceState({}, document.title, newUrl);
            }
        }
    }
    
    // Initialize
    function init() {
        parseCategories();
        
        // Event listeners
        if (searchInput) {
            searchInput.addEventListener('input', debounce(filterCategories, 300));
        }
        
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', resetFilters);
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', filterCategories);
        }
        
        if (resetFiltersBtn) {
            resetFiltersBtn.addEventListener('click', resetFilters);
        }
        
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderCurrentPage();
                }
            });
        }
        
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                const totalPages = Math.ceil(filteredCategories.length / itemsPerPage);
                if (currentPage < totalPages) {
                    currentPage++;
                    renderCurrentPage();
                }
            });
        }
        
        // Attach delete listeners
        attachDeleteListeners();
        
        // Check for highlights
        checkForHighlights();
    }
    
    // Make resetFilters available globally
    window.resetFilters = resetFilters;
    
    // Initialize
    init();
    
    // Log
    console.log('%c📁 Category management initialized', 'color: #7c3aed; font-size: 12px;');
});
