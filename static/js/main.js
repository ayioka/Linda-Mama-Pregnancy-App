// static/js/main.js
// Main application initialization
class LindaMamaApp {
    constructor() {
        this.isAuthenticated = false;
        this.userData = null;
        this.init();
    }
    
    async init() {
        await this.checkAuthStatus();
        this.initializeModules();
        this.setupServiceWorker();
        this.setupErrorHandling();
    }
    
    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status/');
            if (response.ok) {
                const data = await response.json();
                this.isAuthenticated = data.authenticated;
                this.userData = data.user;
                this.updateUIForAuthStatus();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        }
    }
    
    initializeModules() {
        // All modules are initialized via their own files
        // This is the main coordinator
        
        // Add any global event listeners
        this.setupGlobalListeners();
    }
    
    setupGlobalListeners() {
        // Global click handler for analytics
        document.addEventListener('click', this.trackUserInteractions.bind(this));
        
        // Global error handler for forms
        document.addEventListener('submit', this.handleGlobalFormSubmit.bind(this));
        
        // Online/offline detection
        window.addEventListener('online', this.handleOnlineStatus.bind(this));
        window.addEventListener('offline', this.handleOfflineStatus.bind(this));
    }
    
    trackUserInteractions(e) {
        // Basic interaction tracking
        const target = e.target;
        if (target.tagName === 'BUTTON' || target.tagName === 'A') {
            console.log('User interaction:', target.textContent.trim());
        }
    }
    
    handleGlobalFormSubmit(e) {
        // Global form validation can be added here
        const form = e.target;
        if (!form.checkValidity()) {
            e.preventDefault();
            showNotification('Please fill all required fields correctly.', 'warning');
        }
    }
    
    handleOnlineStatus() {
        showNotification('You are back online!', 'success');
    }
    
    handleOfflineStatus() {
        showNotification('You are offline. Some features may not work.', 'warning');
    }
    
    updateUIForAuthStatus() {
        const authElements = document.querySelectorAll('.auth-only');
        const nonAuthElements = document.querySelectorAll('.non-auth-only');
        
        if (this.isAuthenticated) {
            authElements.forEach(el => el.style.display = 'block');
            nonAuthElements.forEach(el => el.style.display = 'none');
        } else {
            authElements.forEach(el => el.style.display = 'none');
            nonAuthElements.forEach(el => el.style.display = 'block');
        }
    }
    
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        }
    }
    
    setupErrorHandling() {
        window.addEventListener('error', this.handleGlobalError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this));
    }
    
    handleGlobalError(event) {
        console.error('Global error:', event.error);
        // You can send errors to your analytics service here
    }
    
    handlePromiseRejection(event) {
        console.error('Unhandled promise rejection:', event.reason);
    }
}

// Initialize the main application
document.addEventListener('DOMContentLoaded', function() {
    window.LindaMamaApp = new LindaMamaApp();
});
