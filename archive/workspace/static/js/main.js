// CleanSignal Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling
    const form = document.getElementById('pollution-form');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/api/incidents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Report submitted successfully!');
                    form.reset();
                    window.location.href = '/dashboard';
                } else {
                    const error = await response.json();
                    alert(error.error || 'Failed to submit report');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Network error. Please try again.');
            }
        });
    }
    
    // Add smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});