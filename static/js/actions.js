// static/js/actions.js
function initializeButtonHandlers() {
    // Action buttons
    const actionButtons = document.querySelectorAll('.btn-action, .cta-button, .primary-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', handleActionButton);
    });
    
    // Emergency button
    const emergencyBtn = document.querySelector('.emergency-btn, [data-action="emergency"]');
    if (emergencyBtn) {
        emergencyBtn.addEventListener('click', handleEmergency);
    }
    
    // Book appointment buttons
    const appointmentBtns = document.querySelectorAll('[data-action="appointment"], .appointment-btn');
    appointmentBtns.forEach(btn => {
        btn.addEventListener('click', handleAppointmentBooking);
    });
}

function initializeFormHandlers() {
    // Contact forms
    const contactForms = document.querySelectorAll('#contact-form, .contact-form');
    contactForms.forEach(form => {
        form.addEventListener('submit', handleContactForm);
    });
    
    // Appointment forms
    const appointmentForms = document.querySelectorAll('#appointment-form, .appointment-form');
    appointmentForms.forEach(form => {
        form.addEventListener('submit', handleAppointmentForm);
    });
    
    // Progress tracking forms
    const progressForms = document.querySelectorAll('#progress-form, .tracking-form');
    progressForms.forEach(form => {
        form.addEventListener('submit', handleProgressTracking);
    });
}

function handleActionButton(e) {
    e.preventDefault();
    const button = e.currentTarget;
    const action = button.getAttribute('data-action') || button.textContent.toLowerCase();
    
    switch(action) {
        case 'book appointment':
        case 'schedule appointment':
            window.location.href = '/appointment/';
            break;
            
        case 'track progress':
        case 'view progress':
            window.location.href = '/progress/';
            break;
            
        case 'get advice':
        case 'health advice':
            window.location.href = '/advice/';
            break;
            
        case 'symptoms checker':
            window.location.href = '/symptoms/';
            break;
            
        case 'nutrition guide':
            window.location.href = '/nutrition/';
            break;
            
        default:
            console.log('Action triggered:', action);
    }
}

function handleEmergency(e) {
    e.preventDefault();
    
    // Show emergency modal or redirect
    if (confirm('This is an emergency feature. Do you want to see emergency contacts?')) {
        window.location.href = '/emergency/';
    }
}

async function handleContactForm(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, 'Sending...');
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const response = await fetch('/api/contact/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
            form.reset();
        } else {
            showNotification(result.error || 'Failed to send message.', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        resetLoading(submitBtn, originalText);
    }
}

async function handleAppointmentForm(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, 'Booking...');
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const response = await fetch('/api/appointments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Appointment booked successfully!', 'success');
            form.reset();
            
            // Redirect to appointments page
            setTimeout(() => {
                window.location.href = '/appointments/';
            }, 2000);
        } else {
            showNotification(result.error || 'Failed to book appointment.', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        resetLoading(submitBtn, originalText);
    }
}

async function handleProgressTracking(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, 'Saving...');
    
    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        const response = await fetch('/api/progress/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Progress saved successfully!', 'success');
            form.reset();
        } else {
            showNotification(result.error || 'Failed to save progress.', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        resetLoading(submitBtn, originalText);
    }
}
