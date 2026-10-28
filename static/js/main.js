/**
 * Prestige Paws NYC - Interactive Frontend Client
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            const isHidden = mobileMenu.classList.contains('hidden');
            if (isHidden) {
                mobileMenu.classList.remove('hidden');
            } else {
                mobileMenu.classList.add('hidden');
            }
        });
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
