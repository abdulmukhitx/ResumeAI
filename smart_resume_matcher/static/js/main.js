// Main JavaScript for Smart Resume Matcher

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const bootstrapAlert = new bootstrap.Alert(alert);
            bootstrapAlert.close();
        });
    }, 5000);
    
    // File input custom text
    const fileInputs = document.querySelectorAll('.form-control[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            const fileSize = this.files[0]?.size;
            
            // Update file name display if element exists
            const fileNameDisplay = document.getElementById('file-name-display');
            if (fileNameDisplay && fileName) {
                fileNameDisplay.textContent = fileName;
            }
            
            // Check file size if it's a resume upload (max 5MB)
            if (fileSize && fileSize > 5 * 1024 * 1024 && this.id === 'id_file') {
                alert('File size exceeds the maximum limit of 5MB. Please choose a smaller file.');
                this.value = '';
            }
        });
    });
    
    // Job search form validation
    const jobSearchForm = document.querySelector('form[action*="job_search"]');
    if (jobSearchForm) {
        jobSearchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('query');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                alert('Please enter a job title, keyword, or company name.');
            }
        });
    }
    
    // Resume analysis progress
    const analysisProgress = document.getElementById('analysis-progress');
    if (analysisProgress) {
        let progress = 0;
        
        // Simulated progress for demo purposes
        const interval = setInterval(function() {
            progress += 5;
            analysisProgress.style.width = progress + '%';
            analysisProgress.setAttribute('aria-valuenow', progress);
            
            if (progress >= 100) {
                clearInterval(interval);
                document.getElementById('analysis-status').textContent = 'Completed';
                document.getElementById('analysis-container').classList.remove('bg-light');
                document.getElementById('analysis-container').classList.add('bg-success', 'text-white');
                
                // Reload the page after a short delay
                setTimeout(function() {
                    window.location.reload();
                }, 1500);
            }
        }, 500);
    }
});

// Function to handle job application form submission
function validateApplication() {
    // Add any validation logic here
    return true;
}

// Function to show/hide skills sections
function toggleSkillsSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.toggle('d-none');
    }
    
    const button = document.querySelector(`[data-target="${sectionId}"]`);
    if (button) {
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        button.setAttribute('aria-expanded', !isExpanded);
        
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-chevron-down');
            icon.classList.toggle('fa-chevron-up');
        }
    }
}
