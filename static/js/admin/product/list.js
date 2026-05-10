// ============================================
// PRODUCTS LIST - MODERN INTERACTIONS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    const stockFilter = document.getElementById('stockFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const tableBody = document.getElementById('productsTableBody');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const startIndexSpan = document.getElementById('startIndex');
    const endIndexSpan = document.getElementById('endIndex');
    const totalCountSpan = document.getElementById('totalCount');
    
    // Variables
    let currentPage = 1;
    let itemsPerPage = 10;
    let filteredProducts = [];
    let allProducts = [];
    let currentSort = { column: null, direction: 'asc' };
    
    // Parse products from table rows
    function parseProducts() {
        const rows = document.querySelectorAll('#productsTableBody tr');
        allProducts = [];
        
        rows.forEach(row => {
            if (row.classList.contains('empty-state')) return;
            
            const product = {
                id: row.dataset.productId,
                name: row.dataset.name,
                nameDisplay: row.querySelector('.product-name')?.textContent || '',
                reference: row.querySelector('.product-reference')?.textContent || '',
                price: parseFloat(row.dataset.price),
                stock: parseInt(row.dataset.stock),
                categoryId: row.dataset.category,
                categoryName: row.dataset.categoryName || 'Non catégorisé',
                status: getStockStatus(parseInt(row.dataset.stock)),
                row: row
            };
            
            allProducts.push(product);
        });
        
        updateStatistics();
        filteredProducts = [...allProducts];
        updateFilteredCount();
        renderCurrentPage();
    }
    
    function getStockStatus(stock) {
        if (stock === 0) return 'out_of_stock';
        if (stock <= 5) return 'low_stock';
        return 'in_stock';
    }
    
    // Update statistics
    function updateStatistics() {
        const inStock = allProducts.filter(p => p.stock > 0).length;
        const lowStock = allProducts.filter(p => p.stock > 0 && p.stock <= 5).length;
        const outOfStock = allProducts.filter(p => p.stock === 0).length;
        
        document.getElementById('inStockCount').textContent = inStock;
        document.getElementById('lowStockCount').textContent = lowStock;
        document.getElementById('outOfStockCount').textContent = outOfStock;
    }
    
    // Filter products
    function filterProducts() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const stockValue = stockFilter.value;
        const categoryValue = categoryFilter.value;
        
        filteredProducts = allProducts.filter(product => {
            // Search filter
            if (searchTerm && !product.name.includes(searchTerm)) {
                return false;
            }
            
            // Stock filter
            if (stockValue !== 'all') {
                if (stockValue === 'in_stock' && product.stock <= 0) return false;
                if (stockValue === 'low_stock' && (product.stock > 5 || product.stock === 0)) return false;
                if (stockValue === 'out_of_stock' && product.stock > 0) return false;
            }
            
            // Category filter
            if (categoryValue !== 'all' && product.categoryId !== categoryValue) {
                return false;
            }
            
            return true;
        });
        
        // Apply sorting
        if (currentSort.column) {
            sortProducts(currentSort.column, currentSort.direction);
        }
        
        updateFilteredCount();
        currentPage = 1;
        renderCurrentPage();
        
        // Show/hide clear search button
        clearSearchBtn.style.display = searchTerm ? 'block' : 'none';
    }
    
    // Sort products
    function sortProducts(column, direction) {
        filteredProducts.sort((a, b) => {
            let aVal, bVal;
            
            switch(column) {
                case 'name':
                    aVal = a.name;
                    bVal = b.name;
                    break;
                case 'price':
                    aVal = a.price;
                    bVal = b.price;
                    break;
                case 'stock':
                    aVal = a.stock;
                    bVal = b.stock;
                    break;
                default:
                    return 0;
            }
            
            if (direction === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });
    }
    
    // Update filter count display
    function updateFilteredCount() {
        const totalCount = filteredProducts.length;
        totalCountSpan.textContent = totalCount;
        
        if (totalCount === 0) {
            showEmptyState();
        } else {
            hideEmptyState();
        }
    }
    
    // Render current page
    function renderCurrentPage() {
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageProducts = filteredProducts.slice(start, end);
        
        // Hide all rows first
        allProducts.forEach(product => {
            product.row.style.display = 'none';
        });
        
        // Show page products
        pageProducts.forEach(product => {
            product.row.style.display = '';
        });
        
        // Update pagination info
        startIndexSpan.textContent = filteredProducts.length > 0 ? start + 1 : 0;
        endIndexSpan.textContent = Math.min(end, filteredProducts.length);
        
        // Update pagination buttons
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = end >= filteredProducts.length;
    }
    
    // Show empty state
    function showEmptyState() {
        let emptyRow = document.querySelector('.empty-state-row');
        if (!emptyRow) {
            emptyRow = document.createElement('tr');
            emptyRow.className = 'empty-state-row';
            emptyRow.innerHTML = `
                <td colspan="6" class="empty-state">
                    <div class="empty-content">
                        <i class="fas fa-box-open"></i>
                        <p>Aucun produit ne correspond à vos critères</p>
                        <button class="btn-reset" id="emptyResetBtn">
                            <i class="fas fa-undo-alt"></i> Réinitialiser les filtres
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(emptyRow);
            
            const emptyResetBtn = emptyRow.querySelector('#emptyResetBtn');
            if (emptyResetBtn) {
                emptyResetBtn.addEventListener('click', resetFilters);
            }
        }
        emptyRow.style.display = '';
        
        allProducts.forEach(product => {
            product.row.style.display = 'none';
        });
    }
    
    function hideEmptyState() {
        const emptyRow = document.querySelector('.empty-state-row');
        if (emptyRow) {
            emptyRow.style.display = 'none';
        }
    }
    
    // Reset filters
    function resetFilters() {
        searchInput.value = '';
        stockFilter.value = 'all';
        categoryFilter.value = 'all';
        clearSearchBtn.style.display = 'none';
        filterProducts();
    }
    
    // Handle sort
    function handleSort(column) {
        const th = document.querySelector(`th[data-sort="${column}"]`);
        const existingSort = th.classList.contains('sort-asc') || th.classList.contains('sort-desc');
        
        // Remove sort classes from all th
        document.querySelectorAll('th.sortable').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        if (existingSort && currentSort.column === column) {
            // Toggle direction
            currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            currentSort.column = column;
            currentSort.direction = 'asc';
        }
        
        // Add class
        th.classList.add(`sort-${currentSort.direction}`);
        
        // Apply sort
        sortProducts(currentSort.column, currentSort.direction);
        currentPage = 1;
        renderCurrentPage();
    }
    
    // Delete product with modal
    function showDeleteModal(productId, productName) {
        const modal = document.getElementById('deleteModal');
        const deleteProductName = document.getElementById('deleteProductName');
        const deleteForm = document.getElementById('deleteForm');
        
        deleteProductName.textContent = productName;
        deleteForm.action = `/admin-panel/products/${productId}/delete/`;
        
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
    
    // Add delete event listeners to all delete buttons
    function attachDeleteListeners() {
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.removeEventListener('click', deleteHandler);
            btn.addEventListener('click', deleteHandler);
        });
    }
    
    function deleteHandler(e) {
        e.preventDefault();
        const productId = this.dataset.id;
        const productName = this.dataset.name;
        showDeleteModal(productId, productName);
    }
    
    // Highligh new/updated product
    function highlightProduct(productId) {
        const row = document.querySelector(`tr[data-product-id="${productId}"]`);
        if (row) {
            row.classList.add('highlight');
            setTimeout(() => {
                row.classList.remove('highlight');
            }, 1000);
        }
    }
    
    // Check for URL parameters (after create/update)
    function checkForHighlights() {
        const urlParams = new URLSearchParams(window.location.search);
        const highlightId = urlParams.get('highlight');
        if (highlightId) {
            highlightProduct(highlightId);
            // Remove from URL without reload
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
        }
    }
    
    // Initialize
    function init() {
        parseProducts();
        
        // Event listeners
        if (searchInput) {
            searchInput.addEventListener('input', debounce(filterProducts, 300));
        }
        
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', resetFilters);
        }
        
        if (stockFilter) {
            stockFilter.addEventListener('change', filterProducts);
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', filterProducts);
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
                const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
                if (currentPage < totalPages) {
                    currentPage++;
                    renderCurrentPage();
                }
            });
        }
        
        // Sort event listeners
        document.querySelectorAll('th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const sortColumn = th.dataset.sort;
                if (sortColumn) {
                    handleSort(sortColumn);
                }
            });
        });
        
        // Attach delete listeners
        attachDeleteListeners();
        
        // Check for highlights
        checkForHighlights();
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
    
    // Initialize everything
    init();
});

// Export for use in other modules if needed
window.ProductList = {
    refresh: () => location.reload(),
    highlight: (id) => {
        const row = document.querySelector(`tr[data-product-id="${id}"]`);
        if (row) {
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 1000);
        }
    }
};