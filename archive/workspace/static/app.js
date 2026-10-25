document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pollution-form');
    const reportsList = document.getElementById('reports-list');

    // Load recent reports on page load
    loadReports();

    // Handle form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const reportData = {
                location: formData.get('location'),
                pollutant_type: formData.get('pollutant_type'),
                severity: formData.get('severity'),
                description: formData.get('description')
            };

            try {
                const response = await fetch('/api/reports', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(reportData)
                });

                if (response.ok) {
                    form.reset();
                    loadReports();
                    alert('Report submitted successfully!');
                } else {
                    alert('Failed to submit report. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Network error. Please check your connection.');
            }
        });
    }

    // Load reports from API
    async function loadReports() {
        try {
            const response = await fetch('/api/reports?limit=5');
            if (response.ok) {
                const reports = await response.json();
                displayReports(reports);
            }
        } catch (error) {
            console.error('Error loading reports:', error);
        }
    }

    // Display reports in grid
    function displayReports(reports) {
        if (!reportsList) return;

        reportsList.innerHTML = reports.map(report => `
            <div class="report-card ${report.severity >= 4 ? 'severe' : ''}">
                <h3>${escapeHtml(report.pollutant_type)}</h3>
                <p><strong>Location:</strong> ${escapeHtml(report.location_name || 'Unknown')}</p>
                <p><strong>Description:</strong> ${escapeHtml(report.description || 'No description')}</p>
                <div class="report-meta">
                    <span>Severity: ${report.severity}/5</span>
                    <span>•</span>
                    <span>${formatDate(report.reported_at)}</span>
                </div>
            </div>
        `).join('');
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Format date
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
});