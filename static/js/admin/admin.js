// ============================================
// MODERN ADMIN DASHBOARD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    
    // ============================================
    // THEME MANAGEMENT
    // ============================================
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    const adminLogo = document.getElementById('adminLogo');
    
    // Load saved theme
    const savedTheme = localStorage.getItem('admin_theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    updateAdminLogo(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('admin_theme', newTheme);
            updateThemeIcon(newTheme);
            updateAdminLogo(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            const label = themeToggle.querySelector('span');
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                if (label) label.textContent = 'Mode clair';
            } else {
                icon.className = 'fas fa-moon';
                if (label) label.textContent = 'Mode sombre';
            }
        }
    }

    function updateAdminLogo(theme) {
        if (!adminLogo) return;
        adminLogo.src = theme === 'dark'
            ? adminLogo.dataset.logoDark
            : adminLogo.dataset.logoLight;
    }
    
    // ============================================
    // SIDEBAR MANAGEMENT
    // ============================================
    const sidebar = document.getElementById('sidebar');
    const sidebarPinBtn = document.getElementById('sidebarPinBtn');
    
    if (sidebar && window.innerWidth > 768) {
        const savedPinnedState = localStorage.getItem('sidebar_pinned') === 'true';
        let isSidebarPinned = savedPinnedState;

        function applySidebarMode() {
            sidebar.classList.toggle('collapsed', !isSidebarPinned);

            if (sidebarPinBtn) {
                sidebarPinBtn.classList.toggle('is-pinned', isSidebarPinned);
                sidebarPinBtn.title = isSidebarPinned ? 'Desactiver le mode fixe' : 'Fixer la sidebar';
                sidebarPinBtn.setAttribute('aria-label', sidebarPinBtn.title);
            }
        }

        applySidebarMode();

        sidebar.addEventListener('mouseenter', () => {
            if (!isSidebarPinned) {
                sidebar.classList.remove('collapsed');
            }
        });
        
        sidebar.addEventListener('mouseleave', () => {
            if (!isSidebarPinned) {
                sidebar.classList.add('collapsed');
            }
        });
        
        sidebar.addEventListener('focusin', () => {
            if (!isSidebarPinned) {
                sidebar.classList.remove('collapsed');
            }
        });
        
        sidebar.addEventListener('focusout', (e) => {
            if (!isSidebarPinned && !sidebar.contains(e.relatedTarget)) {
                sidebar.classList.add('collapsed');
            }
        });

        if (sidebarPinBtn) {
            sidebarPinBtn.addEventListener('click', () => {
                isSidebarPinned = !isSidebarPinned;
                localStorage.setItem('sidebar_pinned', String(isSidebarPinned));
                applySidebarMode();
            });
        }
    }
    
    // ============================================
    // USER DROPDOWN
    // ============================================
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('show');
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && userDropdown.classList.contains('show')) {
                userDropdown.classList.remove('show');
            }
        });
    }
    
    // ============================================
    // NOTIFICATIONS MANAGEMENT
    // ============================================
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach(notification => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            dismissNotification(notification);
        }, 5000);
        
        // Add close button handler
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                dismissNotification(notification);
            });
        }
    });
    
    function dismissNotification(notification) {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
    
    // Add fadeOut animation to styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
    `;
    document.head.appendChild(style);
    
    // ============================================
    // ACTIVE NAVIGATION INDICATOR
    // ============================================
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href)) {
            item.classList.add('active');
        }
    });
    
    // ============================================
    // TOOLTIP SYSTEM (Optional)
    // ============================================
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        if (tooltipText) {
            element.addEventListener('mouseenter', (e) => {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = tooltipText;
                document.body.appendChild(tooltip);
                
                const rect = element.getBoundingClientRect();
                tooltip.style.left = rect.left + rect.width / 2 + 'px';
                tooltip.style.top = rect.top - 30 + 'px';
                tooltip.style.transform = 'translateX(-50%)';
                
                element.addEventListener('mouseleave', () => {
                    tooltip.remove();
                });
            });
        }
    });
    
    // ============================================
    // RESPONSIVE TABLE HANDLING
    // ============================================
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        const container = document.createElement('div');
        container.className = 'table-container';
        table.parentNode.insertBefore(container, table);
        container.appendChild(table);
    });
    
    // ============================================
    // FORM VALIDATION HELPERS
    // ============================================
    window.showNotification = function(message, type = 'info') {
        const container = document.querySelector('.notifications-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 
                     type === 'error' ? 'fa-exclamation-circle' : 
                     'fa-info-circle';
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        container.appendChild(notification);
        
        // Add close handler
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            dismissNotification(notification);
        });
        
        // Auto-dismiss
        setTimeout(() => {
            if (notification.parentNode) {
                dismissNotification(notification);
            }
        }, 5000);
    };
    
    // ============================================
    // LOADING STATE HANDLER
    // ============================================
    window.showLoading = function() {
        let loader = document.querySelector('.global-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'global-loader';
            loader.innerHTML = '<div class="loader-spinner"></div>';
            document.body.appendChild(loader);
            
            // Add loader styles
            const loaderStyle = document.createElement('style');
            loaderStyle.textContent = `
                .global-loader {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                }
                
                .loader-spinner {
                    width: 50px;
                    height: 50px;
                    border: 3px solid var(--border-color);
                    border-top-color: var(--accent-primary);
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }
                
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(loaderStyle);
        }
        loader.style.display = 'flex';
    };
    
    window.hideLoading = function() {
        const loader = document.querySelector('.global-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    };
    
    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================
    document.addEventListener('keydown', (e) => {
        // Ctrl + S to save
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.querySelector('button[type="submit"]');
            if (saveBtn) {
                saveBtn.click();
            }
        }
        
        // Escape to close modals/dropdowns
        if (e.key === 'Escape') {
            const dropdowns = document.querySelectorAll('.user-dropdown.show');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
    
    // ============================================
    // ANIMATE ON SCROLL (optional)
    // ============================================
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // ============================================
    // CONSOLE WELCOME MESSAGE
    // ============================================
    console.log('%c🚀 Me & You Admin Panel', 'color: #7c3aed; font-size: 16px; font-weight: bold;');
    console.log('%cVersion 1.0 | Designed with ❤️', 'color: #06b6d4; font-size: 12px;');
});

// ============================================
// HELPER FUNCTIONS
// ============================================

// Format currency
window.formatCurrency = function(amount, currency = 'EUR') {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

// Format date
window.formatDate = function(date, format = 'dd/mm/yyyy') {
    const d = new Date(date);
    if (format === 'dd/mm/yyyy') {
        return `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getFullYear()}`;
    }
    return d.toLocaleDateString('fr-FR');
};

// Debounce function for search inputs
window.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Handle API errors
window.handleApiError = function(error) {
    console.error('API Error:', error);
    let message = 'Une erreur est survenue';
    
    if (error.response && error.response.data && error.response.data.message) {
        message = error.response.data.message;
    } else if (error.message) {
        message = error.message;
    }
    
    showNotification(message, 'error');
};
