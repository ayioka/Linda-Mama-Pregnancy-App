// static/js/navigation.js
function initializeNavigationHandlers() {
    // Main navigation links
    const navLinks = document.querySelectorAll('nav a, .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
    
    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', toggleBackToTop);
        backToTopBtn.addEventListener('click', scrollToTop);
    }
}

function handleNavigation(e) {
    e.preventDefault();
    const targetUrl = this.getAttribute('href');
    
    if (targetUrl && targetUrl !== '#') {
        // Add smooth page transition
        document.body.style.opacity = '0.7';
        
        setTimeout(() => {
            window.location.href = targetUrl;
        }, 300);
    }
}

function toggleBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}
