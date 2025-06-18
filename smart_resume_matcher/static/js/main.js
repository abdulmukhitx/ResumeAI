// Main JavaScript for Smart Resume Matcher

// GLOBAL REDIRECT PROTECTION - Prevent infinite redirect loops
(function() {
    const REDIRECT_COOLDOWN = 1000; // 1 second between redirects
    let lastRedirectTime = 0;
    
    // Override window.location.href to add protection
    const originalLocationSetter = Object.getOwnPropertyDescriptor(window.location, 'href').set;
    Object.defineProperty(window.location, 'href', {
        set: function(url) {
            const currentTime = Date.now();
            if (currentTime - lastRedirectTime < REDIRECT_COOLDOWN) {
                console.error('🛡️ REDIRECT BLOCKED: Potential infinite redirect loop detected!', {
                    url: url,
                    timeSinceLastRedirect: currentTime - lastRedirectTime,
                    currentPath: window.location.pathname
                });
                return;
            }
            lastRedirectTime = currentTime;
            console.log('✅ Redirect allowed:', url);
            originalLocationSetter.call(this, url);
        },
        get: function() {
            return window.location.toString();
        }
    });
})();

// Enhanced Dark theme functionality
function initializeTheme() {
    // Get theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const defaultTheme = savedTheme || systemTheme;
    
    // Apply theme
    document.documentElement.setAttribute('data-theme', defaultTheme);
    
    // Update toggle button icon
    updateThemeToggleIcon(defaultTheme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            updateThemeToggleIcon(newTheme);
        }
    });
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update button icon
    updateThemeToggleIcon(newTheme);
    
    // Add smooth transition class temporarily
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

function updateThemeToggleIcon(theme) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    const toggleButton = document.getElementById('theme-toggle');
    if (toggleButton) {
        toggleButton.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        toggleButton.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

// Initialize theme immediately
initializeTheme();

// JWT Authentication Initialization
function initializeJWTAuth() {
    // The clean JWT auth manager handles its own initialization
    // Just check if it exists and is working
    if (window.authManager && typeof window.authManager.init === 'function') {
        console.log('✅ Clean JWT Auth Manager is ready');
        
        // Update navigation based on current auth state
        if (window.authManager.isAuthenticated()) {
            console.log('✅ User is authenticated with JWT');
        } else {
            console.log('❌ User is not authenticated');
        }
    } else {
        console.warn('Clean JWT Auth Manager not found! Make sure jwt_auth_clean.js is loaded first.');
        return;
    }
        
    // Listen for authentication events (only if not already set)
    if (!window.authEventsInitialized) {
        window.addEventListener('auth:login', function(event) {
            console.log('🎉 JWT Login successful:', event.detail);
            
            // Update navigation
            if (window.authManager && typeof window.authManager.updateNavigation === 'function') {
                window.authManager.updateNavigation();
            }
            
            // Don't handle redirect here - let the login form handle it
            console.log('Navigation updated after login');
        });
        
        window.addEventListener('auth:logout', function(event) {
            console.log('👋 JWT Logout successful');
            
            // Update navigation
            if (window.authManager && typeof window.authManager.updateNavigation === 'function') {
                window.authManager.updateNavigation();
            }
            // Redirect to login page
            window.location.href = '/login/';
        });
        
        window.authEventsInitialized = true;
    }
        
    // Handle JWT logout buttons
    const logoutButtons = document.querySelectorAll('[data-logout-btn]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                await window.authManager.logout();
            } catch (error) {
                console.error('Logout error:', error);
                // Force logout anyway
                window.authManager.clearTokens();
                window.location.href = '/login/';
            }
        });
    });
}

// JWT Auth will be initialized in DOMContentLoaded event below
// No immediate initialization needed

function updateNavigationForJWT(isAuthenticated) {
    // The clean auth manager handles its own navigation updates
    // This function remains for compatibility but delegates to the auth manager
    if (window.authManager && typeof window.authManager.updateNavigation === 'function') {
        window.authManager.updateNavigation();
    } else {
        // Fallback navigation update
        const authElements = document.querySelectorAll('[data-jwt-auth]');
        authElements.forEach(element => {
            element.style.display = isAuthenticated ? '' : 'none';
        });
        
        const noAuthElements = document.querySelectorAll('[data-jwt-no-auth]');
        noAuthElements.forEach(element => {
            element.style.display = isAuthenticated ? 'none' : '';
        });
    }
}

function handlePageAccess(isAuthenticated) {
    const currentPath = window.location.pathname;
    
    // Handle legacy URL redirects to JWT-compatible URLs
    if (currentPath === '/profile/') {
        console.log('Redirecting from legacy profile URL to JWT profile');
        window.location.href = '/jwt-profile/';
        return;
    }
    
    if (currentPath === '/resume/upload/') {
        console.log('Redirecting from legacy resume upload URL to JWT resume upload');
        window.location.href = '/jwt-resume-upload/';
        return;
    }
    
    // JWT-compatible pages (no authentication required at URL level)
    const jwtPages = ['/jwt-profile/', '/jwt-resume-upload/'];
    const isJWTPage = jwtPages.some(path => currentPath.startsWith(path));
    
    // If user is on login/register page and authenticated, redirect to home
    if (isAuthenticated && (currentPath === '/login/' || currentPath === '/register/')) {
        console.log('User is authenticated, redirecting to home...');
        window.location.href = '/';
        return;
    }
    
    // JWT pages handle their own authentication via JavaScript
    if (isJWTPage) {
        console.log('JWT page detected, authentication handled by page JavaScript');
        return;
    }
}

function updateUserProfileDisplay(userData) {
    // Update user name in dropdown
    const userNameElement = document.getElementById('user-name');
    if (userNameElement && userData.profile) {
        const fullName = userData.profile.full_name || userData.email;
        userNameElement.textContent = fullName;
    }
    
    // Update user avatar
    const userAvatarElement = document.getElementById('user-avatar');
    if (userAvatarElement && userData.profile && userData.profile.profile_picture) {
        userAvatarElement.src = userData.profile.profile_picture;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // IMMEDIATE FAILSAFE: Hide all Django session auth elements
    const djangoAuthElements = document.querySelectorAll('[data-auth-hide]');
    djangoAuthElements.forEach(element => {
        element.style.display = 'none !important';
        element.style.visibility = 'hidden';
    });
    console.log(`🛡️ Failsafe: Hidden ${djangoAuthElements.length} Django auth elements`);
    
    // Initialize JWT Authentication Manager
    initializeJWTAuth();
    
    // Connect to existing theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        
        // Update icon based on current theme
        const currentTheme = document.documentElement.getAttribute('data-theme');
        updateThemeToggleIcon(currentTheme);
    }
    
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
