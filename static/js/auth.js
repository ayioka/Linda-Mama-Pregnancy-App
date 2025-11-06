// static/js/auth.js
document.addEventListener('DOMContentLoaded', function() {
    initializeAllHandlers();
    checkAuthenticationStatus();
});

// Initialize all event handlers
function initializeAllHandlers() {
    initializeAuthHandlers();
    initializeNavigationHandlers();
    initializeButtonHandlers();
    initializeFormHandlers();
}

// Authentication Handlers
function initializeAuthHandlers() {
    // Signup form
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout buttons
    const logoutButtons = document.querySelectorAll('.logout-btn');
    logoutButtons.forEach(btn => {
        btn.addEventListener('click', handleLogout);
    });
}

// Handle Signup
async function handleSignup(e) {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, 'Creating Account...');
    
    try {
        const formData = new FormData(e.target);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password'),
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name')
        };
        
        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Account created successfully! Welcome to Linda Mama!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect_url || '/dashboard/';
            }, 2000);
        } else {
            showNotification(result.error, 'error');
            resetLoading(submitBtn, originalText);
        }
    } catch (error) {
        showNotification('Network error. Please check your connection.', 'error');
        resetLoading(submitBtn, originalText);
    }
}

// Handle Login
async function handleLogin(e) {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, 'Signing In...');
    
    try {
        const formData = new FormData(e.target);
        const data = {
            username: formData.get('username'),
            password: formData.get('password')
        };
        
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect_url || '/dashboard/';
            }, 1000);
        } else {
            showNotification(result.error, 'error');
            resetLoading(submitBtn, originalText);
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
        resetLoading(submitBtn, originalText);
    }
}

// Handle Logout
async function handleLogout(e) {
    e.preventDefault();
    
    try {
        const response = await fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        if (response.ok) {
            showNotification('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}
