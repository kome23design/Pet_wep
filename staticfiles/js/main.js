/**
 * Prestige Paws NYC - Interactive Frontend Client
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isHidden = mobileMenu.classList.contains('hidden');
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
            } else {
                mobileMenu.classList.add('hidden');
            }
        });

        // Close mobile menu if clicked outside
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });

        // Close mobile menu when any nav link inside is clicked
        mobileMenu.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
            });
        });
    }

    // Dynamic Navbar Spacer calculation to ensure fixed navbar never overlaps page content
    function updateNavbarSpacer() {
        const topBar = document.getElementById('top-concierge-bar');
        const header = document.querySelector('#site-navbar > header');
        const spacer = document.getElementById('navbar-spacer');
        if (spacer && header) {
            const topBarHeight = topBar ? topBar.offsetHeight : 0;
            const headerHeight = header.offsetHeight;
            spacer.style.height = (topBarHeight + headerHeight) + 'px';
        }
    }

    updateNavbarSpacer();
    window.addEventListener('resize', updateNavbarSpacer);
    window.addEventListener('orientationchange', updateNavbarSpacer);
    window.addEventListener('load', updateNavbarSpacer);

    // Elevated shadow on fixed navbar when scrolled
    const siteNavbar = document.getElementById('site-navbar');
    if (siteNavbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 15) {
                siteNavbar.classList.add('shadow-md');
            } else {
                siteNavbar.classList.remove('shadow-md');
            }
        }, { passive: true });
    }

    // Auto-dismiss alert banners after 6 seconds
    const alerts = document.querySelectorAll('.alert-banner');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        }, 6000);
    });

    // Newsletter quick AJAX submission
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    newsletterForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = form.querySelector('input[name="email"]');
            const submitBtn = form.querySelector('button[type="submit"]');
            const feedback = form.querySelector('.newsletter-feedback');
            
            if (!emailInput || !emailInput.value) return;

            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Subscribing...';

            const formData = new FormData();
            formData.append('email', emailInput.value);

            fetch('/newsletter/subscribe/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    emailInput.value = '';
                    if (feedback) {
                        feedback.textContent = '✓ Subscribed to VIP Pet Placement updates.';
                        feedback.className = 'newsletter-feedback text-sm text-green-700 mt-2 font-medium';
                    }
                    submitBtn.innerHTML = 'Subscribed!';
                } else {
                    if (feedback) {
                        feedback.textContent = data.error || 'Unable to subscribe.';
                        feedback.className = 'newsletter-feedback text-sm text-red-600 mt-2';
                    }
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
            })
            .catch(() => {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            });
        });
    });
});

// CSRF helper for AJAX requests
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

// Universal password visibility toggle for all forms requiring password
function initPasswordVisibilityToggles() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(function(input) {
        if (input.dataset.hasToggle) return;
        input.dataset.hasToggle = 'true';

        // Check if there is already a toggle button next to it
        const parent = input.parentElement;
        if (!parent.classList.contains('relative')) {
            parent.classList.add('relative');
        }

        input.style.paddingRight = '2.75rem';

        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'pwd-toggle-btn absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-forest focus:outline-none transition-colors p-1 z-10';
        toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
        toggleBtn.innerHTML = '<i class="fa-regular fa-eye text-sm"></i>';

        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (input.type === 'password') {
                input.type = 'text';
                toggleBtn.innerHTML = '<i class="fa-regular fa-eye-slash text-sm text-gold-dark"></i>';
            } else {
                input.type = 'password';
                toggleBtn.innerHTML = '<i class="fa-regular fa-eye text-sm"></i>';
            }
        });

        input.insertAdjacentElement('afterend', toggleBtn);
    });
}

document.addEventListener('DOMContentLoaded', initPasswordVisibilityToggles);
