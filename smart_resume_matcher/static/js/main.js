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
    console.log('🌙 Toggle theme function called');
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    console.log('Current theme:', currentTheme);
    console.log('New theme:', newTheme);
    
    // Apply new theme
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    console.log('Theme applied to document, data-theme is now:', document.documentElement.getAttribute('data-theme'));
    
    // Update button icon
    updateThemeToggleIcon(newTheme);
    
    // Update button colors for dark theme
    const button = document.getElementById('theme-toggle');
    if (button) {
        if (newTheme === 'dark') {
            button.style.background = 'linear-gradient(135deg, #FFD700, #FFA500) !important';
            button.style.borderColor = 'rgba(255, 215, 0, 0.4) !important';
            button.style.boxShadow = '0 4px 12px rgba(255, 215, 0, 0.4) !important';
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.style.color = '#1a1a1a !important';
            }
        } else {
            button.style.background = 'linear-gradient(135deg, #8c43ff, #7938d6) !important';
            button.style.borderColor = 'rgba(255, 255, 255, 0.3) !important';
            button.style.boxShadow = '0 4px 12px rgba(140, 67, 255, 0.4) !important';
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.style.color = '#ffffff !important';
            }
        }
    }
    
    // Add smooth transition class temporarily
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
    
    console.log('✅ Theme toggle completed');
}

function updateThemeToggleIcon(theme) {
    console.log('🎨 Updating theme icon for theme:', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    console.log('Theme icon element:', themeIcon);
    
    if (themeIcon) {
        const newIcon = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        themeIcon.className = newIcon;
        console.log('Updated icon class to:', newIcon);
    } else {
        console.error('❌ Theme icon element not found!');
    }
    
    const toggleButton = document.getElementById('theme-toggle');
    if (toggleButton) {
        const tooltipText = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
        toggleButton.setAttribute('title', tooltipText);
        toggleButton.setAttribute('aria-label', tooltipText);
        console.log('Updated button tooltip:', tooltipText);
    } else {
        console.error('❌ Theme toggle button not found for icon update!');
    }
}

function setupThemeToggle() {
    console.log('🎯 Setting up theme toggle...');
    
    // Find the theme toggle button
    let themeToggle = document.getElementById('theme-toggle');
    console.log('Theme toggle element:', themeToggle);
    
    // EMERGENCY FIX: If button doesn't exist or is not working, create/fix it
    if (!themeToggle || themeToggle.offsetWidth === 0) {
        console.log('🚨 Emergency theme toggle fix needed...');
        themeToggle = emergencyThemeToggleFix();
    }
    
    if (themeToggle) {
        console.log('✅ Theme toggle button found/created');
        
        // Define the click handler function inline to ensure it exists
        const clickHandler = function(event) {
            console.log('🔘 Theme toggle clicked!', event);
            
            // Prevent default behavior
            event.preventDefault();
            event.stopPropagation();
            
            // Call the toggle function
            toggleTheme();
        };
        
        // Remove any existing listeners to avoid duplicates
        themeToggle.removeEventListener('click', clickHandler);
        
        // Add multiple event listeners to ensure it works
        themeToggle.addEventListener('click', clickHandler);
        themeToggle.addEventListener('mousedown', clickHandler);
        
        // Also add onclick as fallback
        themeToggle.onclick = clickHandler;
        
        // Store the handler for later removal if needed
        themeToggle._clickHandler = clickHandler;
        
        // Update icon based on current theme
        const currentTheme = document.documentElement.getAttribute('data-theme');
        console.log('Current theme when setting up button:', currentTheme);
        updateThemeToggleIcon(currentTheme);
        
        console.log('✅ Theme toggle setup complete');
    } else {
        console.error('❌ Theme toggle button could not be created or found!');
    }
}

// EMERGENCY THEME TOGGLE FIX - Permanent solution
function emergencyThemeToggleFix() {
    console.log('🔧 EMERGENCY THEME TOGGLE FIX');
    
    // Find or create button
    let button = document.getElementById('theme-toggle');
    
    if (!button) {
        console.log('Creating new theme toggle button...');
        button = document.createElement('button');
        button.id = 'theme-toggle';
        button.className = 'theme-toggle';
        button.setAttribute('type', 'button');
        button.setAttribute('aria-label', 'Toggle theme');
        button.setAttribute('title', 'Toggle dark/light mode');
        button.innerHTML = '<i class="fas fa-moon" id="theme-icon"></i>';
        
        // Try to add to navbar first
        const navbar = document.querySelector('.navbar .navbar-nav');
        if (navbar) {
            const li = document.createElement('li');
            li.className = 'nav-item d-flex align-items-center';
            li.appendChild(button);
            navbar.appendChild(li);
            console.log('✅ Button added to navbar');
        } else {
            // Fallback: add to body as fixed position
            document.body.appendChild(button);
            button.style.position = 'fixed';
            button.style.top = '20px';
            button.style.right = '20px';
            console.log('✅ Button added to body (fixed position)');
        }
    }
    
    // Force proper styling regardless of CSS conflicts
    button.style.cssText = `
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: linear-gradient(135deg, #8c43ff, #7938d6) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        z-index: 99999 !important;
        position: relative !important;
        font-size: 1.2rem !important;
        margin: 0 10px !important;
        padding: 0 !important;
        box-shadow: 0 4px 12px rgba(140, 67, 255, 0.4) !important;
        transition: all 0.3s ease !important;
        outline: none !important;
    `;
    
    // Ensure icon styling
    const icon = button.querySelector('i');
    if (icon) {
        icon.style.cssText = `
            color: white !important;
            font-size: 1.2rem !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        `;
    }
    
    // Add hover effects
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
        this.style.boxShadow = '0 6px 20px rgba(140, 67, 255, 0.6)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 4px 12px rgba(140, 67, 255, 0.4)';
    });
    
    console.log('✅ Emergency theme toggle fix applied!');
    return button;
}

// DEBUG FUNCTION: Test dark mode toggle manually
window.testDarkMode = function() {
    console.log('🧪 MANUAL DARK MODE TEST');
    console.log('Current theme:', document.documentElement.getAttribute('data-theme'));
    
    const button = document.getElementById('theme-toggle');
    console.log('Button element:', button);
    
    if (button) {
        console.log('Button click handler:', button._clickHandler);
        console.log('Calling toggleTheme() directly...');
        toggleTheme();
    } else {
        console.error('Button not found!');
    }
};

// Initialize theme immediately
console.log('🎨 Script loaded, initializing theme immediately...');
initializeTheme();

// Also set up theme toggle immediately if DOM is already ready
if (document.readyState === 'loading') {
    console.log('⏳ DOM is still loading, will setup theme toggle on DOMContentLoaded');
} else {
    console.log('✅ DOM already loaded, setting up theme toggle immediately');
    setupThemeToggle();
}

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
    console.log('🚀 DOM Content Loaded - Starting initialization...');
    
    // IMMEDIATE FAILSAFE: Hide all Django session auth elements
    const djangoAuthElements = document.querySelectorAll('[data-auth-hide]');
    djangoAuthElements.forEach(element => {
        element.style.display = 'none !important';
        element.style.visibility = 'hidden';
    });
    console.log(`🛡️ Failsafe: Hidden ${djangoAuthElements.length} Django auth elements`);
    
    // Initialize JWT Authentication Manager
    initializeJWTAuth();
    
    // Setup theme toggle with enhanced debugging
    console.log('🎨 Setting up theme toggle...');
    setupThemeToggle();
    
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

// CONSOLE DEBUG FUNCTIONS - Use these in browser console to debug issues
window.debugTheme = function() {
    console.log('🔧 THEME DEBUG INFORMATION');
    console.log('Current theme:', document.documentElement.getAttribute('data-theme'));
    console.log('Saved theme:', localStorage.getItem('theme'));
    
    const button = document.getElementById('theme-toggle');
    console.log('Theme button:', button);
    
    const icon = document.getElementById('theme-icon');
    console.log('Theme icon:', icon);
    
    if (button) {
        console.log('Button classes:', button.className);
        console.log('Button style.display:', button.style.display);
        console.log('Button offsetWidth:', button.offsetWidth);
        console.log('Button offsetHeight:', button.offsetHeight);
    }
    
    if (icon) {
        console.log('Icon classes:', icon.className);
    }
};

window.forceThemeToggleSetup = function() {
    console.log('🔧 FORCING THEME TOGGLE SETUP');
    setupThemeToggle();
};

window.testThemeToggle = function() {
    console.log('🧪 TESTING THEME TOGGLE');
    toggleTheme();
};

// EMERGENCY CONSOLE FIX - Run this in console if button still doesn't work after reload
window.emergencyThemeFix = function() {
    console.log('🚨 RUNNING EMERGENCY THEME FIX FROM CONSOLE');
    
    // Remove any existing broken buttons
    const existingButtons = document.querySelectorAll('#theme-toggle, .theme-toggle');
    existingButtons.forEach(btn => btn.remove());
    
    // Create new button
    const button = document.createElement('button');
    button.id = 'theme-toggle';
    button.className = 'theme-toggle';
    button.setAttribute('type', 'button');
    button.setAttribute('aria-label', 'Toggle theme');
    button.setAttribute('title', 'Toggle dark/light mode');
    button.innerHTML = '<i class="fas fa-moon" id="theme-icon"></i>';
    
    // Style button
    button.style.cssText = `
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: linear-gradient(135deg, #8c43ff, #7938d6) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        z-index: 99999 !important;
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 12px rgba(140, 67, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    `;
    
    // Add click handler
    button.onclick = function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            icon.style.color = newTheme === 'dark' ? '#1a1a1a' : '#ffffff';
        }
        
        // Update button style for dark theme
        if (newTheme === 'dark') {
            this.style.background = 'linear-gradient(135deg, #FFD700, #FFA500)';
            this.style.borderColor = 'rgba(255, 215, 0, 0.4)';
            this.style.boxShadow = '0 4px 12px rgba(255, 215, 0, 0.4)';
        } else {
            this.style.background = 'linear-gradient(135deg, #8c43ff, #7938d6)';
            this.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            this.style.boxShadow = '0 4px 12px rgba(140, 67, 255, 0.4)';
        }
        
        console.log('✅ Theme changed to:', newTheme);
    };
    
    // Add hover effects
    button.onmouseover = function() {
        this.style.transform = 'scale(1.1)';
    };
    button.onmouseout = function() {
        this.style.transform = 'scale(1)';
    };
    
    // Add to page
    document.body.appendChild(button);
    
    console.log('✅ Emergency theme button created! Look for it in the top-right corner.');
    return button;
};
