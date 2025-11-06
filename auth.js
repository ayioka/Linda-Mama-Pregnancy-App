// Handle Signup Form
document.addEventListener('DOMContentLoaded', function() {
    // Signup form handler
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
    
    // Login form handler
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Add click handlers to all buttons
    initializeButtonHandlers();
});

async function handleSignup(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        confirm_password: formData.get('confirm_password')
    };
    
    try {
        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Account created successfully! Welcome to Linda Mama!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 2000);
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('An error occurred. Please try again.', 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect_url;
            }, 1000);
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('An error occurred. Please try again.', 'error');
    }
}

// Initialize all button handlers
function initializeButtonHandlers() {
    // Navigation buttons
    const navButtons = document.querySelectorAll('nav a, .nav-button');
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href');
            if (target) {
                window.location.href = target;
            }
        });
    });
    
    // Action buttons
    const actionButtons = document.querySelectorAll('.btn-action, .submit-btn, .cta-button');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.type !== 'submit') {
                e.preventDefault();
                handleActionButton(this);
            }
        });
    });
}

function handleActionButton(button) {
    const action = button.getAttribute('data-action') || button.textContent.toLowerCase();
    
    switch(action) {
        case 'book appointment':
            window.location.href = '/appointment/';
            break;
        case 'track progress':
            window.location.href = '/progress/';
            break;
        case 'get advice':
            window.location.href = '/advice/';
            break;
        case 'emergency':
            window.location.href = '/emergency/';
            break;
        default:
            console.log('Button action:', action);
    }
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        z-index: 1000;
        font-weight: bold;
        transition: opacity 0.3s;
        ${type === 'success' ? 'background: #4CAF50;' : ''}
        ${type === 'error' ? 'background: #f44336;' : ''}
        ${type === 'info' ? 'background: #2196F3;' : ''}
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}
