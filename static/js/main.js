/**
 * H.C. Lombardo App - Main JavaScript
 * Client-side functionality for the H.C. Lombardo application
 */

// H.C. Lombardo App Namespace
const HCLombardo = {
    // Configuration
    config: {
        apiBaseUrl: window.location.origin,
        themes: ['nfl', 'text', 'corporate', 'dark'],
        currentTheme: 'default'
    },

    // Initialize the application
    init() {
        console.log('🚀 H.C. Lombardo App Initializing...');
        this.setupEventListeners();
        this.loadTheme();
        this.animateElements();
        this.checkApiStatus();
        console.log('✅ H.C. Lombardo App Ready!');
    },

    // Setup event listeners
    setupEventListeners() {
        // Navigation card hover effects
        document.querySelectorAll('.nav-card').forEach(card => {
            card.addEventListener('mouseenter', this.onCardHover.bind(this));
            card.addEventListener('mouseleave', this.onCardLeave.bind(this));
            card.addEventListener('click', this.onCardClick.bind(this));
        });

        // Theme switcher
        const themeSwitcher = document.getElementById('theme-switcher');
        if (themeSwitcher) {
            themeSwitcher.addEventListener('change', this.switchTheme.bind(this));
        }

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', this.onQuickAction.bind(this));
        });

        // API status refresh
        const statusRefresh = document.getElementById('refresh-status');
        if (statusRefresh) {
            statusRefresh.addEventListener('click', this.checkApiStatus.bind(this));
        }
    },

    // Handle navigation card hover
    onCardHover(event) {
        const card = event.currentTarget;
        card.style.transform = 'translateY(-8px) scale(1.02)';
        card.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.3)';
        
        // Add ripple effect
        this.addRippleEffect(card, event);
    },

    // Handle navigation card leave
    onCardLeave(event) {
        const card = event.currentTarget;
        card.style.transform = '';
        card.style.boxShadow = '';
    },

    // Handle navigation card click
    onCardClick(event) {
        const card = event.currentTarget;
        const url = card.getAttribute('href');
        
        if (url && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            this.navigateWithAnimation(url);
        }
    },

    // Add ripple effect to elements
    addRippleEffect(element, event) {
        const ripple = document.createElement('div');
        ripple.classList.add('ripple');
        
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        element.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    },

    // Navigate with smooth animation
    navigateWithAnimation(url) {
        document.body.style.opacity = '0.8';
        document.body.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            window.location.href = url;
        }, 200);
    },

    // Switch application theme
    switchTheme(event) {
        const theme = event.target.value;
        this.config.currentTheme = theme;
        
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        if (theme !== 'default') {
            document.body.classList.add(`theme-${theme}`);
        }
        
        localStorage.setItem('hc-lombardo-theme', theme);
        this.showNotification(`Theme switched to ${theme.toUpperCase()}`, 'success');
    },

    // Load saved theme
    loadTheme() {
        const savedTheme = localStorage.getItem('hc-lombardo-theme');
        if (savedTheme && this.config.themes.includes(savedTheme)) {
            this.config.currentTheme = savedTheme;
            document.body.classList.add(`theme-${savedTheme}`);
            
            const themeSwitcher = document.getElementById('theme-switcher');
            if (themeSwitcher) {
                themeSwitcher.value = savedTheme;
            }
        }
    },

    // Animate elements on page load
    animateElements() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe navigation cards
        document.querySelectorAll('.nav-card').forEach(card => {
            observer.observe(card);
        });

        // Observe feature items
        document.querySelectorAll('.feature-item').forEach(item => {
            observer.observe(item);
        });
    },

    // Check API status
    async checkApiStatus() {
        const statusElement = document.querySelector('.api-status');
        if (!statusElement) return;

        statusElement.textContent = '🔄 Checking API Status...';
        statusElement.className = 'api-status status-warning';

        try {
            const response = await fetch(`${this.config.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (response.ok && data.status === 'healthy') {
                statusElement.textContent = '🟢 API Online';
                statusElement.className = 'api-status status-online';
            } else {
                throw new Error('API not healthy');
            }
        } catch (error) {
            statusElement.textContent = '🔴 API Offline';
            statusElement.className = 'api-status status-offline';
            console.warn('API Status Check Failed:', error);
        }
    },

    // Handle quick actions
    onQuickAction(event) {
        const action = event.currentTarget.getAttribute('data-action');
        
        switch (action) {
            case 'docs':
                window.open(`${this.config.apiBaseUrl}/docs`, '_blank');
                break;
            case 'redoc':
                window.open(`${this.config.apiBaseUrl}/redoc`, '_blank');
                break;
            case 'github':
                window.open('https://github.com/AprilV/H.C.-Lombardo-App', '_blank');
                break;
            case 'refresh':
                location.reload();
                break;
            default:
                console.log('Unknown quick action:', action);
        }
    },

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // Utility functions
    utils: {
        // Format timestamp
        formatTime(timestamp) {
            return new Date(timestamp).toLocaleString();
        },

        // Debounce function calls
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        // Copy text to clipboard
        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                HCLombardo.showNotification('Copied to clipboard!', 'success');
            } catch (error) {
                console.error('Failed to copy:', error);
                HCLombardo.showNotification('Failed to copy', 'error');
            }
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    HCLombardo.init();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        HCLombardo.checkApiStatus();
    }
});

// Export for use in other scripts
window.HCLombardo = HCLombardo;