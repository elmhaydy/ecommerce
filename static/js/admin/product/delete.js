// ============================================
// DELETE CONFIRMATION - FINAL VERSION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    
    // DOM Elements
    const confirmCheckbox = document.getElementById('confirmCheckbox');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const deleteForm = document.getElementById('deleteForm');
    const cancelBtn = document.getElementById('cancelBtn');
    const deleteContainer = document.querySelector('.delete-container');
    
    // Activer/Désactiver le bouton de confirmation
    if (confirmCheckbox && confirmDeleteBtn) {
        confirmCheckbox.addEventListener('change', (e) => {
            confirmDeleteBtn.disabled = !e.target.checked;
            
            // Animation sur le bouton quand activé
            if (e.target.checked) {
                confirmDeleteBtn.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    confirmDeleteBtn.style.transform = '';
                }, 200);
                
                // Ajouter une classe pour le style
                confirmDeleteBtn.classList.add('ready');
            } else {
                confirmDeleteBtn.classList.remove('ready');
            }
        });
    }
    
    // Gérer la soumission du formulaire
    if (deleteForm) {
        deleteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!confirmCheckbox?.checked) {
                showNotification('Veuillez confirmer la suppression en cochant la case', 'warning');
                return;
            }
            
            await submitDelete();
        });
    }
    
    // Fonction de soumission avec animation
    async function submitDelete() {
        const submitBtn = document.querySelector('.btn-danger');
        const originalHTML = submitBtn.innerHTML;
        
        // Désactiver le bouton et afficher le chargement
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Suppression en cours...';
        
        // Animation de fondu
        if (deleteContainer) {
            deleteContainer.style.transition = 'opacity 0.3s ease';
            deleteContainer.style.opacity = '0.7';
        }
        
        // Petit délai pour l'animation (optionnel)
        setTimeout(() => {
            // Soumettre le formulaire
            deleteForm.submit();
        }, 500);
    }
    
    // Notification system
    function showNotification(message, type) {
        // Chercher ou créer le conteneur de notifications
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-circle';
        if (type === 'warning') icon = 'fa-exclamation-triangle';
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        container.appendChild(notification);
        
        // Auto-suppression après 5 secondes
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Bouton de fermeture
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            });
        }
    }
    
    // Gestion du raccourci clavier ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const cancelUrl = cancelBtn?.getAttribute('href');
            if (cancelUrl) {
                window.location.href = cancelUrl;
            }
        }
    });
    
    // Effet de brillance périodique sur le bouton quand prêt
    let glowInterval;
    
    if (confirmCheckbox) {
        confirmCheckbox.addEventListener('change', (e) => {
            if (e.target.checked && confirmDeleteBtn && !confirmDeleteBtn.disabled) {
                glowInterval = setInterval(() => {
                    if (confirmDeleteBtn && !confirmDeleteBtn.disabled && confirmCheckbox.checked) {
                        confirmDeleteBtn.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.5)';
                        setTimeout(() => {
                            if (confirmDeleteBtn) confirmDeleteBtn.style.boxShadow = '';
                        }, 300);
                    }
                }, 2000);
            } else if (glowInterval) {
                clearInterval(glowInterval);
            }
        });
    }
    
    // Log de démarrage
    console.log('%c🗑️ Delete confirmation page ready', 'color: #ef4444; font-size: 12px; font-weight: bold;');
    
    // Animation de compteur de sécurité (optionnel - 3 secondes avant activation)
    let secondsLeft = 3;
    const countdownElement = document.createElement('span');
    
    if (confirmDeleteBtn && confirmDeleteBtn.disabled) {
        const updateCountdown = () => {
            if (secondsLeft > 0) {
                confirmDeleteBtn.innerHTML = `<i class="fas fa-trash-alt"></i> <span>Attendez ${secondsLeft}s...</span>`;
                secondsLeft--;
                setTimeout(updateCountdown, 1000);
            } else {
                confirmDeleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> <span>Supprimer définitivement</span>';
                if (confirmCheckbox?.checked) {
                    confirmDeleteBtn.disabled = false;
                }
            }
        };
        // Décommenter la ligne suivante pour activer le compte à rebours de sécurité
        // updateCountdown();
    }
});

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { showNotification: window.showNotification };
}