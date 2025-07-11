/**
 * Clean JWT Authentication Manager for Smart Resume Matcher
 * 
 * This is a simplified, robust implementation that avoids console errors
 * and initialization conflicts while maintaining all JWT functionality.
 */

class CleanJWTAuth {
    constructor() {
        this.baseURL = window.location.origin;
        this.accessTokenKey = 'smart_resume_access_token';
        this.refreshTokenKey = 'smart_resume_refresh_token';
        this.userDataKey = 'smart_resume_user_data';
        this.isRefreshing = false;
        this.initializationTimestamp = Date.now();
        
        // Bind methods to preserve context
        this.login = this.login.bind(this);
        this.logout = this.logout.bind(this);
        this.refreshAccessToken = this.refreshAccessToken.bind(this);
        this.authenticatedFetch = this.authenticatedFetch.bind(this);
    }

    // Token Management
    getAccessToken() {
        return localStorage.getItem(this.accessTokenKey);
    }

    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    setTokens(accessToken, refreshToken) {
        // Store in localStorage (for JavaScript access)
        localStorage.setItem(this.accessTokenKey, accessToken);
        if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
        }
        
        // CRITICAL FIX: Also store in cookies (for server middleware access)
        this.setCookie('access_token', accessToken, 1); // 1 day expiry
        if (refreshToken) {
            this.setCookie('refresh_token', refreshToken, 7); // 7 days expiry
        }
        
        console.log('✅ JWT tokens stored in both localStorage and cookies');
    }

    clearTokens() {
        // Clear localStorage
        localStorage.removeItem(this.accessTokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userDataKey);
        
        // CRITICAL FIX: Also clear cookies
        this.deleteCookie('access_token');
        this.deleteCookie('refresh_token');
        
        console.log('🧹 JWT tokens cleared from both localStorage and cookies');
    }
    
    // Cookie management helper methods
    setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        const secure = window.location.protocol === 'https:' ? '; secure' : '';
        document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/; SameSite=Lax${secure}`;
    }
    
    deleteCookie(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }
    
    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // User Data Management
    getCurrentUser() {
        const userData = localStorage.getItem(this.userDataKey);
        return userData ? JSON.parse(userData) : null;
    }

    setUserData(userData) {
        localStorage.setItem(this.userDataKey, JSON.stringify(userData));
    }

    // Authentication Status
    isAuthenticated() {
        const accessToken = this.getAccessToken();
        const refreshToken = this.getRefreshToken();
        return !!(accessToken && refreshToken);
    }

    // Get Options (for compatibility)
    getOptions() {
        return {
            authenticated: this.isAuthenticated(),
            user: this.getCurrentUser(),
            accessToken: this.getAccessToken(),
            refreshToken: this.getRefreshToken()
        };
    }

    // Alias for getCurrentUser (for compatibility)
    getUserData() {
        return this.getCurrentUser();
    }

    // Login
    async login(email, password) {
        try {
            // Use 'email' field to authenticate via JWT endpoint (our serializer expects email field)
            const credentials = { email: email, password };
            const response = await fetch(`${this.baseURL}/api/auth/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || errorData.error || errorData.non_field_errors?.[0] || 'Login failed';
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Store tokens and user data
            this.setTokens(data.access, data.refresh);
            this.setUserData(data.user);
            
            // Dispatch login event
            this.dispatchAuthEvent('login', data.user);
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    // Logout
    async logout() {
        const refreshToken = this.getRefreshToken();
        
        if (refreshToken) {
            try {
                // Attempt to blacklist token on server
                await fetch(`${this.baseURL}/api/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh: refreshToken })
                });
            } catch (error) {
                // Silent fail for logout endpoint - still clear local tokens
                console.warn('Logout endpoint error (continuing with local logout):', error);
            }
        }
        
        // Clear local storage
        this.clearTokens();
        
        // Dispatch logout event
        this.dispatchAuthEvent('logout');
    }

    // Token Refresh
    async refreshAccessToken() {
        if (this.isRefreshing) {
            // Wait for ongoing refresh
            return new Promise((resolve, reject) => {
                const checkRefresh = () => {
                    if (!this.isRefreshing) {
                        const newToken = this.getAccessToken();
                        if (newToken) {
                            resolve(newToken);
                        } else {
                            reject(new Error('Token refresh failed'));
                        }
                    } else {
                        setTimeout(checkRefresh, 100);
                    }
                };
                checkRefresh();
            });
        }

        this.isRefreshing = true;
        
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

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
            this.setTokens(data.access, data.refresh);
            
            return data.access;
        } catch (error) {
            console.warn('Token refresh failed, logging out:', error);
            this.logout();
            throw error;
        } finally {
            this.isRefreshing = false;
        }
    }

    // Authenticated Fetch
    async authenticatedFetch(url, options = {}) {
        let accessToken = this.getAccessToken();
        
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
            let response = await fetch(url, config);
            
            // Handle token expiration
            if (response.status === 401) {
                try {
                    accessToken = await this.refreshAccessToken();
                    config.headers['Authorization'] = `Bearer ${accessToken}`;
                    response = await fetch(url, config);
                } catch (refreshError) {
                    throw new Error('Authentication failed');
                }
            }
            
            return response;
        } catch (error) {
            // Only log significant errors
            if (!error.message.includes('No access token available') &&
                !error.message.includes('Authentication failed')) {
                console.error('Authenticated fetch error:', error);
            }
            throw error;
        }
    }

    // Token Verification (only when explicitly called)
    async verifyToken() {
        try {
            const response = await this.authenticatedFetch(`${this.baseURL}/api/auth/verify/`);
            
            if (response.ok) {
                const userData = await response.json();
                this.setUserData(userData);
                return userData;
            } else {
                throw new Error('Token verification failed');
            }
        } catch (error) {
            console.warn('Token verification failed:', error);
            this.logout();
            throw error;
        }
    }

    // Event System
    dispatchAuthEvent(eventType, data = null) {
        const event = new CustomEvent(`auth:${eventType}`, { 
            detail: data,
            bubbles: true
        });
        window.dispatchEvent(event);
    }

    // Navigation Updates (called manually, not automatically)
    updateNavigation() {
        const isAuth = this.isAuthenticated();
        const user = this.getCurrentUser();
        
        console.log('🔄 Updating navigation:', { isAuth, userEmail: user?.email });
        
        // FORCE HIDE all Django session-based auth elements (failsafe)
        const djangoAuthElements = document.querySelectorAll('[data-auth-hide]');
        console.log(`Found ${djangoAuthElements.length} Django auth elements to hide`);
        djangoAuthElements.forEach(element => {
            element.style.display = 'none !important';
            element.style.visibility = 'hidden';
        });
        
        // Show/hide JWT authenticated elements
        const authElements = document.querySelectorAll('[data-jwt-auth]');
        console.log(`Found ${authElements.length} JWT auth elements`);
        authElements.forEach(element => {
            element.style.display = isAuth ? '' : 'none';
        });
        
        // Show/hide JWT non-authenticated elements
        const noAuthElements = document.querySelectorAll('[data-jwt-no-auth]');
        console.log(`Found ${noAuthElements.length} JWT no-auth elements`);
        noAuthElements.forEach(element => {
            element.style.display = isAuth ? 'none' : '';
        });
        
        // Update user info if authenticated
        if (isAuth && user) {
            const userNameElement = document.getElementById('user-name');
            const userEmailElement = document.getElementById('user-email');
            
            if (userNameElement) {
                userNameElement.textContent = user.first_name || user.username || 'User';
                console.log('✅ Updated user name element');
            }
            if (userEmailElement) {
                userEmailElement.textContent = user.email || '';
                console.log('✅ Updated user email element');
            }
        }
        
        console.log('✅ Navigation update completed');
    }

    // Initialize (minimal setup, no automatic calls)
    init() {
        console.log('🔐 Clean JWT Auth Manager initialized');
        
        // Update navigation based on current authentication state
        this.updateNavigation();
        
        // If user is authenticated, log the status
        if (this.isAuthenticated()) {
            const userData = this.getCurrentUser();
            console.log('✅ User authenticated on page load:', userData?.email || 'Unknown');
        } else {
            console.log('❌ User not authenticated on page load');
        }
        
        return this;
    }
}

// Create single global instance only if it doesn't exist
if (!window.authManager || window.authManager.initializationTimestamp < (Date.now() - 1000)) {
    window.authManager = new CleanJWTAuth();
    console.log('✨ Clean JWT Auth Manager created');
}

// Initialize when DOM is ready (only once)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.authManager && typeof window.authManager.init === 'function') {
            window.authManager.init();
        }
    });
} else {
    // DOM already loaded
    if (window.authManager && typeof window.authManager.init === 'function') {
        window.authManager.init();
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CleanJWTAuth;
}
