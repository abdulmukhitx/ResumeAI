/**
 * Simplified JWT Authentication Handler for Smart Resume Matcher
 * 
 * This provides a clean JWT authentication system without automatic
 * initialization conflicts or duplicate API calls.
 */

class SimpleJWTAuth {
    constructor() {
        this.baseURL = window.location.origin;
        this.accessTokenKey = 'smart_resume_access_token';
        this.refreshTokenKey = 'smart_resume_refresh_token';
        this.userDataKey = 'smart_resume_user_data';
    }

    /**
     * Login user with email and password
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
            this.dispatchEvent('login', data.user);
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * Logout user
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
        
        // Trigger logout event
        this.dispatchEvent('logout');
        
        // Redirect to login page
        window.location.href = '/login/';
    }

    /**
     * Make authenticated API request
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
                try {
                    const newToken = await this.refreshAccessToken();
                    config.headers['Authorization'] = `Bearer ${newToken}`;
                    return await fetch(url, config);
                } catch (refreshError) {
                    this.logout();
                    throw refreshError;
                }
            }
            
            return response;
        } catch (error) {
            throw error;
        }
    }

    /**
     * Refresh access token
     */
    async refreshAccessToken() {
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
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Get access token from storage
     */
    getAccessToken() {
        return localStorage.getItem(this.accessTokenKey);
    }

    /**
     * Get refresh token from storage
     */
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    /**
     * Store tokens securely
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
     */
    setUserData(userData) {
        localStorage.setItem(this.userDataKey, JSON.stringify(userData));
    }

    /**
     * Get current user data
     */
    getCurrentUser() {
        const userData = localStorage.getItem(this.userDataKey);
        return userData ? JSON.parse(userData) : null;
    }

    /**
     * Clear stored user data
     */
    clearUserData() {
        localStorage.removeItem(this.userDataKey);
    }

    /**
     * Dispatch authentication events
     */
    dispatchEvent(eventType, data = null) {
        const event = new CustomEvent(`auth:${eventType}`, { 
            detail: data 
        });
        window.dispatchEvent(event);
    }
}

// Create single global instance
if (!window.authManager) {
    window.authManager = new SimpleJWTAuth();
    console.log('🔐 Simple JWT Auth Manager created');
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimpleJWTAuth;
}
