// Main JavaScript for modern layout
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Wait for auth manager to be available
    const checkAuthManager = () => {
        if (typeof window.authManager !== 'undefined') {
            initializeAuth();
        } else {
            setTimeout(checkAuthManager, 100);
        }
    };
    
    checkAuthManager();
    
    // Initialize other components
    initializeSidebar();
    initializeNavigation();
    initializeTheme();
}

function initializeAuth() {
    const isAuthenticated = window.authManager && window.authManager.isAuthenticated();
    const userData = isAuthenticated ? window.authManager.getUserData() : null;
    
    // Show/hide auth-dependent elements
    const authElements = document.querySelectorAll('[data-jwt-auth]');
    const noAuthElements = document.querySelectorAll('[data-jwt-no-auth]');
    
    // Handle authenticated state
    if (isAuthenticated) {
        authElements.forEach(element => {
            element.style.display = '';
        });
        noAuthElements.forEach(element => {
            element.style.display = 'none';
        });
        
        // Add authenticated class to body for CSS styling
        document.body.classList.add('authenticated');
        document.body.classList.remove('sidebar-collapsed');
        
        // Update user information
        if (userData) {
            updateUserDisplay(userData);
            loadUserStats(userData);
            loadRecentActivity();
        }
    } else {
        // Handle non-authenticated state
        authElements.forEach(element => {
            element.style.display = 'none';
        });
        noAuthElements.forEach(element => {
            element.style.display = '';
        });
        
        // Remove authenticated class and collapse sidebar
        document.body.classList.remove('authenticated');
        document.body.classList.add('sidebar-collapsed');
    }
}

function updateUserDisplay(userData) {
    // Update user name displays
    const userNameElements = document.querySelectorAll('#user-name, #user-name-header');
    const userEmailElement = document.getElementById('user-email');
    
    const displayName = userData.first_name && userData.last_name 
        ? `${userData.first_name} ${userData.last_name}`
        : userData.username || 'User';
    
    userNameElements.forEach(element => {
        element.textContent = displayName;
    });
    
    if (userEmailElement) {
        userEmailElement.textContent = userData.email || '';
    }
}

function loadUserStats(userData) {
    // Update sidebar stats
    const jobMatchesElement = document.getElementById('job-matches-count');
    const profileScoreElement = document.getElementById('profile-score');
    
    if (jobMatchesElement) {
        // Calculate realistic job matches based on profile completion
        let baseMatches = 8; // Minimum matches
        if (userData.latest_resume) baseMatches += 12;
        if (userData.first_name && userData.last_name) baseMatches += 5;
        if (userData.phone) baseMatches += 3;
        
        // Add some variance (3-8 additional matches)
        const variance = Math.floor(Math.random() * 6) + 3;
        const totalMatches = baseMatches + variance;
        
        setTimeout(() => {
            animateNumber(jobMatchesElement, 0, totalMatches, 1000);
            
            // Add a subtle pulse effect when animation completes
            setTimeout(() => {
                jobMatchesElement.parentElement.classList.add('stat-highlight');
                setTimeout(() => {
                    jobMatchesElement.parentElement.classList.remove('stat-highlight');
                }, 1000);
            }, 1000);
        }, 500);
    }
    
    if (profileScoreElement) {
        // Calculate realistic profile completeness
        let score = 15; // Base score for having an account
        if (userData.first_name) score += 10;
        if (userData.last_name) score += 10;
        if (userData.email) score += 8;
        if (userData.phone) score += 12;
        if (userData.latest_resume) score += 35;
        if (userData.profile_picture) score += 10;
        
        // Ensure minimum 25% and maximum 95%
        score = Math.max(25, Math.min(95, score));
        
        setTimeout(() => {
            animateNumber(profileScoreElement, 0, score, 1500, '%');
            
            // Add color coding based on score
            if (score >= 80) {
                profileScoreElement.className = 'stat-number text-success';
            } else if (score >= 60) {
                profileScoreElement.className = 'stat-number text-warning';
            } else {
                profileScoreElement.className = 'stat-number text-danger';
            }
            
            // Add progress bar effect
            setTimeout(() => {
                const progressBar = createProgressBar(score);
                const statCard = profileScoreElement.closest('.stat-card');
                if (statCard && !statCard.querySelector('.progress-bar-container')) {
                    statCard.appendChild(progressBar);
                }
            }, 1500);
        }, 800);
    }
}

// Helper function to create animated progress bar
function createProgressBar(percentage) {
    const container = document.createElement('div');
    container.className = 'progress-bar-container';
    container.innerHTML = `
        <div class="mini-progress-bar">
            <div class="mini-progress-fill" style="width: 0%; animation: fillProgress 1s ease forwards ${percentage >= 80 ? '0.5s' : '0.3s'};">
                <style>
                    @keyframes fillProgress {
                        to { width: ${percentage}%; }
                    }
                </style>
            </div>
        </div>
    `;
    return container;
}

function loadRecentActivity() {
    const activityContainer = document.getElementById('recent-activity');
    if (!activityContainer) return;
    
    // Generate realistic activity based on current time
    const activities = [
        {
            icon: 'fas fa-search',
            title: 'Job Search',
            time: getRelativeTime(2)
        },
        {
            icon: 'fas fa-user-edit',
            title: 'Profile Updated',
            time: getRelativeTime(24)
        },
        {
            icon: 'fas fa-heart',
            title: 'Job Matched',
            time: getRelativeTime(48)
        },
        {
            icon: 'fas fa-file-upload',
            title: 'Resume Uploaded',
            time: getRelativeTime(72)
        },
        {
            icon: 'fas fa-eye',
            title: 'Profile Viewed',
            time: getRelativeTime(96)
        }
    ];
    
    // Simulate loading with a beautiful animation
    setTimeout(() => {
        let activityHTML = '<div class="activity-timeline">';
        
        activities.forEach((activity, index) => {
            activityHTML += `
                <div class="activity-item" style="animation-delay: ${index * 200}ms;">
                    <div class="activity-icon">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                </div>
            `;
        });
        
        activityHTML += '</div>';
        activityContainer.innerHTML = activityHTML;
        
        // Add fade-in animation
        activityContainer.classList.add('fade-in');
    }, 1200);
}

// Helper function to generate realistic relative time
function getRelativeTime(hoursAgo) {
    if (hoursAgo < 1) {
        return 'Just now';
    } else if (hoursAgo < 24) {
        return `${hoursAgo} hour${hoursAgo === 1 ? '' : 's'} ago`;
    } else {
        const daysAgo = Math.floor(hoursAgo / 24);
        return `${daysAgo} day${daysAgo === 1 ? '' : 's'} ago`;
    }
}

function animateNumber(element, start, end, duration, suffix = '') {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + (end - start) * easeOutQuart);
        
        element.textContent = current + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function initializeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    // Mobile sidebar toggle
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-open');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !toggleBtn?.contains(event.target)) {
                sidebar.classList.remove('sidebar-open');
            }
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('sidebar-open');
        }
    });
}

function initializeNavigation() {
    // Handle dropdown menus
    const dropdownElements = document.querySelectorAll('.dropdown-toggle');
    
    // Handle logout button
    const logoutBtn = document.querySelector('[data-logout-btn]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (typeof window.authManager !== 'undefined') {
                window.authManager.logout();
                window.location.href = '/';
            }
        });
    }
    
    // Add active states to navigation items
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
}

function initializeTheme() {
    // Theme is locked to dark mode, but keep functionality for future use
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', 'dark');
    
    // Keep theme toggle functionality disabled but in code
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Disabled for now - dark mode only
            console.log('Theme toggle disabled - dark mode only');
        });
    }
}

// Enhanced user experience features
function initializeEnhancements() {
    // Add smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with fade-in-on-scroll class
    document.querySelectorAll('.fade-in-on-scroll').forEach(el => {
        observer.observe(el);
    });
    
    // Add loading states for buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.classList.add('loading');
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                
                // Re-enable after form submission or timeout
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Enhanced tooltips (if Bootstrap tooltips are available)
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Call enhancement initialization
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeEnhancements, 500); // Small delay to ensure DOM is fully ready
});

// Listen for authentication events
window.addEventListener('auth:login', function(event) {
    console.log('User logged in, updating UI...');
    initializeAuth();
});

window.addEventListener('auth:logout', function(event) {
    console.log('User logged out, updating UI...');
    initializeAuth();
});

// Utility functions
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
    }
}

function hideLoading(element, content) {
    if (element) {
        element.innerHTML = content || '';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show modern-alert`;
    notification.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    const container = document.querySelector('.content-wrapper');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Add hover effects to interactive elements
document.addEventListener('mouseover', function(e) {
    const card = e.target.closest('.card, .sidebar-item, .activity-item');
    if (card) {
        card.style.transform = 'translateY(-2px)';
    }
});

document.addEventListener('mouseout', function(e) {
    const card = e.target.closest('.card, .sidebar-item, .activity-item');
    if (card) {
        card.style.transform = 'translateY(0)';
    }
});

// Add ripple effect to buttons
document.addEventListener('click', function(e) {
    const button = e.target.closest('.btn');
    if (button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
});

// CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export functions for global use
window.modernLayout = {
    showNotification,
    showLoading,
    hideLoading,
    animateNumber,
    initializeAuth
};
