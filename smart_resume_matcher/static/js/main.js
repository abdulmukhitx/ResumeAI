// Main JavaScript for Smart Resume Matcher

// Dark theme functionality
function initializeTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Update toggle button icon
    updateThemeToggleIcon(currentTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    updateThemeToggleIcon(newTheme);
}

function updateThemeToggleIcon(theme) {
    const toggleButton = document.getElementById('theme-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        toggleButton.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

// Initialize theme on page load
initializeTheme();

document.addEventListener('DOMContentLoaded', function() {
    // Add theme toggle button to the page
    const themeToggle = document.createElement('button');
    themeToggle.id = 'theme-toggle';
    themeToggle.className = 'theme-toggle';
    themeToggle.setAttribute('aria-label', 'Toggle dark mode');
    themeToggle.addEventListener('click', toggleTheme);
    document.body.appendChild(themeToggle);
    
    // Update icon based on current theme
    const currentTheme = document.documentElement.getAttribute('data-theme');
    updateThemeToggleIcon(currentTheme);
    
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
