// CleanSignal Frontend Application

class CleanSignalApp {
    constructor() {
        this.apiBaseUrl = '/api';
        this.reports = [];
        this.init();
    }

    async init() {
        this.bindEvents();
        this.loadReports();
        this.checkAuth();
    }

    bindEvents() {
        // Form submission
        document.getElementById('report-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitReport();
        });

        // Login button
        document.getElementById('auth-btn').addEventListener('click', () => {
            this.showLoginModal();
        });

        // Scroll to reports
        window.scrollToReports = () => {
            document.getElementById('reports').scrollIntoView({ behavior: 'smooth' });
        };
    }

    async submitReport() {
        const form = document.getElementById('report-form');
        const formData = new FormData(form);
        
        const reportData = {
            location: formData.get('location'),
            description: formData.get('description'),
            pollutant_type: formData.get('pollutant_type') || null,
            severity: parseInt(formData.get('severity'))
        };

        try {
            // In production, use fetch with token
            const response = await fetch(`${this.apiBaseUrl}/reports`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reportData)
            });

            if (!response.ok) throw new Error('Failed to submit report');
            
            const result = await response.json();
            this.showSuccess('Report submitted successfully!');
            form.reset();
            this.loadReports();
        } catch (error) {
            console.error('Submit error:', error);
            this.showError('Failed to submit report. Please try again.');
        }
    }

    async loadReports() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/reports`);
            if (!response.ok) throw new Error('Failed to load reports');
            
            const data = await response.json();
            this.reports = data.reports;
            this.renderReports();
        } catch (error) {
            console.error('Load error:', error);
            document.getElementById('reports-container').innerHTML = `
                <div class="spinner"></div>
                <p>Loading reports...</p>
            `;
        }
    }

    renderReports() {
        const container = document.getElementById('reports-container');
        
        if (this.reports.length === 0) {
            container.innerHTML = '<p>No reports yet. Be the first to report pollution!</p>';
            return;
        }

        container.innerHTML = this.reports.map(report => `
            <div class="report-card">
                <div class="report-header">
                    <span class="report-location">📍 ${this.escapeHtml(report.location)}</span>
                    <span class="report-type">${this.escapeHtml(report.pollutant_type || 'General')}</span>
                </div>
                <p class="report-description">${this.escapeHtml(report.description)}</p>
                <div class="report-meta">
                    <span>📅 ${new Date(report.timestamp).toLocaleDateString()}</span>
                    <span class="severity-badge severity-${report.severity >= 4 ? '4-5' : report.severity}">
                        Severity: ${report.severity}/5
                    </span>
                </div>
            </div>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showSuccess(message) {
        const msg = document.createElement('div');
        msg.className = 'success-message';
        msg.style.display = 'block';
        msg.textContent = message;
        
        // Insert before form
        const formContainer = document.getElementById('reports');
        formContainer.insertBefore(msg, formContainer.querySelector('.report-form'));
        
        setTimeout(() => { msg.style.display = 'none'; }, 5000);
    }

    showError(message) {
        const msg = document.createElement('div');
        msg.className = 'error-message';
        msg.style.display = 'block';
        msg.textContent = message;
        
        const formContainer = document.getElementById('reports');
        formContainer.insertBefore(msg, formContainer.querySelector('.report-form'));
        
        setTimeout(() => { msg.style.display = 'none'; }, 5000);
    }

    showLoginModal() {
        // Simple login modal implementation
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Login to CleanSignal</h3>
                <p>Enter your credentials to continue.</p>
                <input type="email" placeholder="Email" style="margin: 10px 0; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">
                <input type="password" placeholder="Password" style="margin: 10px 0; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">
                <button class="btn-primary" onclick="this.closest('.modal').remove();">Login</button>
            </div>
        `;
        document.body.appendChild(modal);
    }

    checkAuth() {
        // Check for existing token in localStorage
        const token = localStorage.getItem('auth_token');
        if (token) {
            document.getElementById('auth-btn').textContent = 'Logout';
            document.getElementById('auth-btn').onclick = () => {
                localStorage.removeItem('auth_token');
                location.reload();
            };
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CleanSignalApp();
});