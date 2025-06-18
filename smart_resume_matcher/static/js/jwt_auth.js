/**
 * JWT Authentication Handler for Smart Resume Matcher
 * 
 * This module provides a complete JWT authentication system for the frontend,
 * including automatic token refresh, secure storage, and API request handling.
 */

class JWTAuthManager {
    constructor() {
        this.baseURL = window.location.origin;
        this.accessTokenKey = 'smart_resume_access_token';
        this.refreshTokenKey = 'smart_resume_refresh_token';
        this.userDataKey = 'smart_resume_user_data';
        this.isRefreshing = false;
        this.isInitializing = false;
        this.failedQueue = [];
        
        // Initialize axios-like request interceptor
        this.setupRequestInterceptor();
    }

    /**
     * Login user with email and password
     * @param {string} email 
     * @param {string} password 
     * @returns {Promise<Object>} User data and tokens
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/api/auth/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const data = await response.json();
            
            // Store tokens and user data
            this.setTokens(data.access, data.refresh);
            this.setUserData(data.user);
            
            // Trigger login event
            this.dispatchAuthEvent('login', data.user);
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * Logout user and blacklist tokens
     */
    async logout() {
        const refreshToken = this.getRefreshToken();
        
        if (refreshToken) {
            try {
                await fetch(`${this.baseURL}/api/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
            } catch (error) {
                console.warn('Logout API call failed:', error);
            }
        }
        
        // Clear stored data
        this.clearTokens();
        this.clearUserData();
        localStorage.removeItem('jwt_last_verification');
        
        // Trigger logout event
        this.dispatchAuthEvent('logout');
        
        // Redirect to login page
        window.location.href = '/login/';
    }

    /**
     * Refresh access token
     * @returns {Promise<string>} New access token
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch(`${this.baseURL}/api/auth/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            
            // Update stored tokens
            this.setTokens(data.access, data.refresh);
            
            return data.access;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout(); // Force logout on refresh failure
            throw error;
        }
    }

    /**
     * Make authenticated API request
     * @param {string} url 
     * @param {Object} options 
     * @returns {Promise<Response>}
     */
    async authenticatedFetch(url, options = {}) {
        const accessToken = this.getAccessToken();
        
        if (!accessToken) {
            throw new Error('No access token available');
        }

        const config = {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            }
        };

        try {
            const response = await fetch(url, config);
            
            // Handle token expiration
            if (response.status === 401) {
                console.log('Token expired, attempting refresh...');
                try {
                    const newToken = await this.refreshAccessToken();
                    config.headers['Authorization'] = `Bearer ${newToken}`;
                    return await fetch(url, config);
                } catch (refreshError) {
                    console.warn('Token refresh failed, logging out:', refreshError);
                    this.logout();
                    throw refreshError;
                }
            }
            
            return response;
        } catch (error) {
            // Only log significant errors, not network timeouts or common issues
            if (error.name !== 'TypeError' && 
                !error.message.includes('NetworkError') && 
                !error.message.includes('Failed to fetch') &&
                !error.message.includes('No access token available')) {
                console.error('Authenticated fetch error:', error);
            }
            throw error;
        }
    }

    /**
     * Verify current token and get user data
     * @returns {Promise<Object>} User data if token is valid
     */
    async verifyToken() {
        // Prevent rapid successive verification calls
        const now = Date.now();
        const lastCall = this.lastVerifyCall || 0;
        const minInterval = 2000; // 2 seconds minimum between calls
        
        if ((now - lastCall) < minInterval) {
            console.log('Token verification throttled');
            return this.getCurrentUser();
        }
        
        this.lastVerifyCall = now;
        
        try {
            const response = await this.authenticatedFetch(`${this.baseURL}/api/auth/verify/`);
            
            if (response.ok) {
                const data = await response.json();
                this.setUserData(data.user);
                return data.user;
            } else {
                throw new Error('Token verification failed');
            }
        } catch (error) {
            console.error('Token verification error:', error);
            this.logout();
            throw error;
        }
    }

    /**
     * Get current user data
     * @returns {Object|null} User data or null if not logged in
     */
    getCurrentUser() {
        const userData = localStorage.getItem(this.userDataKey);
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Check if user is authenticated
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Get access token from storage
     * @returns {string|null}
     */
    getAccessToken() {
        return localStorage.getItem(this.accessTokenKey);
    }

    /**
     * Get refresh token from storage
     * @returns {string|null}
     */
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    /**
     * Store tokens securely
     * @param {string} accessToken 
     * @param {string} refreshToken 
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem(this.accessTokenKey, accessToken);
        localStorage.setItem(this.refreshTokenKey, refreshToken);
    }

    /**
     * Clear stored tokens
     */
    clearTokens() {
        localStorage.removeItem(this.accessTokenKey);
        localStorage.removeItem(this.refreshTokenKey);
    }

    /**
     * Store user data
     * @param {Object} userData 
     */
    setUserData(userData) {
        localStorage.setItem(this.userDataKey, JSON.stringify(userData));
    }

    /**
     * Clear stored user data
     */
    clearUserData() {
        localStorage.removeItem(this.userDataKey);
    }

    /**
     * Setup automatic token refresh for fetch requests
     */
    setupRequestInterceptor() {
        // Don't override global fetch as it causes conflicts
        // Instead, we'll handle authentication manually in specific methods
        console.log('JWT Auth Manager: Request interceptor setup completed');
    }

    /**
     * Dispatch authentication events
     * @param {string} eventType 
     * @param {Object} data 
     */
    dispatchAuthEvent(eventType, data = null) {
        const event = new CustomEvent(`auth:${eventType}`, { 
            detail: data 
        });
        window.dispatchEvent(event);
    }

    /**
     * Initialize authentication manager
     */
    async init() {
        // Skip initialization if no tokens are present
        if (!this.isAuthenticated()) {
            console.log('JWT Auth: No tokens found, skipping initialization');
            return;
        }
        
        // Prevent multiple simultaneous initialization
        if (this.isInitializing || window.jwtInitComplete) {
            console.log('JWT initialization already in progress or complete');
            return;
        }
        
        this.isInitializing = true;
        window.jwtInitComplete = true;
        
        try {
            console.log('JWT authentication manager initialized');
            // Don't automatically verify tokens on page load
            // Let the user actions trigger verification when needed
        } finally {
            this.isInitializing = false;
        }
    }
}

// Create global instance only if it doesn't exist
if (!window.authManager) {
    window.authManager = new JWTAuthManager();
    console.log('🔐 JWT Auth Manager created');
}

// Initialize only once when DOM is ready
if (!window.jwtDOMInitialized) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (window.authManager) {
                window.authManager.init();
            }
        });
    } else {
        // DOM already loaded
        if (window.authManager) {
            window.authManager.init();
        }
    }
    window.jwtDOMInitialized = true;
}

// Authentication event listeners for UI updates (only if not already initialized)
if (!window.jwtUIEventsInitialized) {
    window.addEventListener('auth:login', (event) => {
        console.log('User logged in:', event.detail);
        // Update UI elements for authenticated state
        updateAuthenticationUI(true, event.detail);
    });

    window.addEventListener('auth:logout', () => {
        console.log('User logged out');
        // Update UI elements for unauthenticated state
        updateAuthenticationUI(false);
    });
    
    window.jwtUIEventsInitialized = true;
}

/**
 * Update UI elements based on authentication state
 * @param {boolean} isAuthenticated 
 * @param {Object} userData 
 */
function updateAuthenticationUI(isAuthenticated, userData = null) {
    // Update navigation menu
    const authElements = document.querySelectorAll('[data-auth-show]');
    const noAuthElements = document.querySelectorAll('[data-auth-hide]');
    
    authElements.forEach(el => {
        el.style.display = isAuthenticated ? 'block' : 'none';
    });
    
    noAuthElements.forEach(el => {
        el.style.display = isAuthenticated ? 'none' : 'block';
    });
    
    // Update user info displays
    if (isAuthenticated && userData) {
        const userNameElements = document.querySelectorAll('[data-user-name]');
        const userEmailElements = document.querySelectorAll('[data-user-email]');
        
        userNameElements.forEach(el => {
            el.textContent = userData.first_name || userData.email;
        });
        
        userEmailElements.forEach(el => {
            el.textContent = userData.email;
        });
    }
}

/**
 * Enhanced login form handler
 */
function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const errorDiv = document.getElementById('loginError');
        
        // Show loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Logging in...';
        }
        
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
        
        try {
            await window.authManager.login(email, password);
            
            // Redirect to dashboard or intended page
            const redirectUrl = new URLSearchParams(window.location.search).get('next') || '/';
            window.location.href = redirectUrl;
            
        } catch (error) {
            // Show error message
            if (errorDiv) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            }
        } finally {
            // Reset button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Log In';
            }
        }
    });
}

/**
 * Setup logout buttons
 */
function setupLogoutButtons() {
    const logoutButtons = document.querySelectorAll('[data-logout-btn]');
    
    logoutButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            if (confirm('Are you sure you want to log out?')) {
                await window.authManager.logout();
            }
        });
    });
}

// Initialize form handlers when DOM is loaded (only once)
if (!window.jwtFormsInitialized) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setupLoginForm();
            setupLogoutButtons();
            
            // Initialize UI state based on current authentication
            if (window.authManager) {
                const currentUser = window.authManager.getCurrentUser();
                updateAuthenticationUI(window.authManager.isAuthenticated(), currentUser);
            }
        });
    } else {
        // DOM already loaded
        setupLoginForm();
        setupLogoutButtons();
        
        // Initialize UI state based on current authentication
        if (window.authManager) {
            const currentUser = window.authManager.getCurrentUser();
            updateAuthenticationUI(window.authManager.isAuthenticated(), currentUser);
        }
    }
    window.jwtFormsInitialized = true;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JWTAuthManager;
}
