// static/js/dashboard.js
class DashboardManager {
    constructor() {
        this.userData = null;
        this.init();
    }
    
    async init() {
        await this.loadUserData();
        this.initializeDashboardWidgets();
        this.setupRealTimeUpdates();
    }
    
    async loadUserData() {
        try {
            const response = await fetch('/api/user/profile/');
            if (response.ok) {
                this.userData = await response.json();
                this.updateDashboardUI();
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }
    
    initializeDashboardWidgets() {
        // Pregnancy week tracker
        this.initPregnancyTracker();
        
        // Next appointment widget
        this.initAppointmentWidget();
        
        // Symptoms tracker
        this.initSymptomsTracker();
        
        // Weight tracker
        this.initWeightTracker();
    }
    
    initPregnancyTracker() {
        const weekElement = document.getElementById('current-week');
        const progressElement = document.getElementById('pregnancy-progress');
        
        if (weekElement && this.userData && this.userData.pregnancy_week) {
            weekElement.textContent = `Week ${this.userData.pregnancy_week}`;
            
            if (progressElement) {
                const progress = (this.userData.pregnancy_week / 40) * 100;
                progressElement.style.width = `${progress}%`;
                progressElement.setAttribute('aria-valuenow', progress);
            }
        }
    }
    
    initAppointmentWidget() {
        const appointmentElement = document.getElementById('next-appointment');
        
        if (appointmentElement) {
            // Fetch next appointment
            this.fetchNextAppointment().then(appointment => {
                if (appointment) {
                    appointmentElement.innerHTML = `
                        <strong>${appointment.doctor}</strong><br>
                        ${appointment.date} at ${appointment.time}<br>
                        <small>${appointment.location}</small>
                    `;
                } else {
                    appointmentElement.innerHTML = 'No upcoming appointments';
                }
            });
        }
    }
    
    async fetchNextAppointment() {
        try {
            const response = await fetch('/api/appointments/next/');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to fetch appointments:', error);
        }
        return null;
    }
    
    initSymptomsTracker() {
        const symptomsForm = document.getElementById('symptoms-form');
        if (symptomsForm) {
            symptomsForm.addEventListener('submit', this.handleSymptomsSubmit.bind(this));
        }
    }
    
    async handleSymptomsSubmit(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch('/api/symptoms/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showNotification('Symptoms recorded successfully', 'success');
                e.target.reset();
            }
        } catch (error) {
            showNotification('Failed to record symptoms', 'error');
        }
    }
    
    initWeightTracker() {
        const weightChart = document.getElementById('weight-chart');
        if (weightChart) {
            this.renderWeightChart();
        }
    }
    
    async renderWeightChart() {
        try {
            const response = await fetch('/api/weight-history/');
            if (response.ok) {
                const data = await response.json();
                // Initialize chart here (you can use Chart.js or similar)
                this.createSimpleWeightChart(data);
            }
        } catch (error) {
            console.error('Failed to load weight history:', error);
        }
    }
    
    createSimpleWeightChart(data) {
        // Simple chart implementation
        const chartElement = document.getElementById('weight-chart');
        if (chartElement && data.length > 0) {
            // Basic chart rendering logic
            chartElement.innerHTML = '<div class="chart-placeholder">Weight tracking chart will be displayed here</div>';
        }
    }
    
    setupRealTimeUpdates() {
        // Update dashboard every 5 minutes
        setInterval(() => {
            this.loadUserData();
        }, 300000);
    }
    
    updateDashboardUI() {
        // Update various dashboard elements with user data
        const welcomeElement = document.getElementById('welcome-message');
        if (welcomeElement && this.userData) {
            welcomeElement.textContent = `Welcome, ${this.userData.first_name || 'Mama'}!`;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('dashboard')) {
        new DashboardManager();
    }
});
