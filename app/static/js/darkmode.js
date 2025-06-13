/**
 * Dark Mode Toggle Functionality
 * Bautagebuch App - Borrmann Professionals
 */

class DarkModeManager {
    constructor() {
        this.storageKey = 'bautagebuch-theme';
        this.defaultTheme = 'light';
        this.currentTheme = this.getStoredTheme();
        
        this.init();
    }

    init() {
        // Apply stored theme immediately to prevent flash
        this.applyTheme(this.currentTheme);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupToggle());
        } else {
            this.setupToggle();
        }
    }

    getStoredTheme() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored && ['light', 'dark'].includes(stored)) {
                return stored;
            }
        } catch (e) {
            console.warn('Could not access localStorage for theme preference');
        }

        // Fallback to system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        return this.defaultTheme;
    }

    setStoredTheme(theme) {
        try {
            localStorage.setItem(this.storageKey, theme);
        } catch (e) {
            console.warn('Could not save theme preference to localStorage');
        }
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        // Set theme color based on current theme
        const colors = {
            light: '#2c5aa0', // Primary blue
            dark: '#0f172a'   // Dark background
        };
        
        metaThemeColor.content = colors[theme] || colors.light;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.setStoredTheme(newTheme);
        
        // Update toggle button state
        this.updateToggleButton();
        
        // Show toast notification
        if (window.BautagebuchApp && window.BautagebuchApp.showToast) {
            const message = newTheme === 'dark' ? 'Dark Mode aktiviert' : 'Light Mode aktiviert';
            window.BautagebuchApp.showToast(message, 'info', 2000);
        }
    }

    setupToggle() {
        // Create toggle button if it doesn't exist
        this.createToggleButton();
        
        // Update button state
        this.updateToggleButton();
        
        // Listen for system theme changes
        this.listenForSystemThemeChanges();
    }

    createToggleButton() {
        // Check if toggle already exists
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        // Find the user menu in navigation
        const userMenu = document.querySelector('.flex.items-center.space-x-4');
        if (!userMenu) {
            console.warn('Could not find user menu to add theme toggle');
            return;
        }

        // Create toggle container
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'flex items-center';
        
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'theme-toggle';
        toggleButton.setAttribute('aria-label', 'Theme umschalten');
        toggleButton.setAttribute('title', 'Zwischen Light und Dark Mode wechseln');
        
        // Create slider
        const slider = document.createElement('div');
        slider.className = 'theme-toggle-slider';
        
        // Add icons
        this.updateSliderIcon(slider, this.currentTheme);
        
        toggleButton.appendChild(slider);
        toggleContainer.appendChild(toggleButton);
        
        // Insert before user menu
        userMenu.insertBefore(toggleContainer, userMenu.firstChild);
        
        // Add click event
        toggleButton.addEventListener('click', () => this.toggleTheme());
        
        // Add keyboard support
        toggleButton.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    updateToggleButton() {
        const slider = document.querySelector('.theme-toggle-slider');
        if (slider) {
            this.updateSliderIcon(slider, this.currentTheme);
        }
        
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            const newTitle = this.currentTheme === 'light' 
                ? 'Zu Dark Mode wechseln' 
                : 'Zu Light Mode wechseln';
            toggle.setAttribute('title', newTitle);
        }
    }

    updateSliderIcon(slider, theme) {
        // Use Lucide icons if available, otherwise use emoji
        if (window.lucide) {
            slider.innerHTML = theme === 'light' 
                ? '<i data-lucide="sun" class="w-4 h-4"></i>'
                : '<i data-lucide="moon" class="w-4 h-4"></i>';
            
            // Recreate icons
            if (window.lucide.createIcons) {
                window.lucide.createIcons();
            }
        } else {
            slider.textContent = theme === 'light' ? '☀️' : '🌙';
        }
    }

    listenForSystemThemeChanges() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleChange = (e) => {
                // Only auto-switch if user hasn't manually set a preference
                const hasManualPreference = localStorage.getItem(this.storageKey);
                if (!hasManualPreference) {
                    const systemTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(systemTheme);
                    this.updateToggleButton();
                }
            };
            
            // Modern browsers
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', handleChange);
            } else {
                // Fallback for older browsers
                mediaQuery.addListener(handleChange);
            }
        }
    }

    // Public API methods
    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            this.applyTheme(theme);
            this.setStoredTheme(theme);
            this.updateToggleButton();
        }
    }

    resetToSystemPreference() {
        localStorage.removeItem(this.storageKey);
        const systemTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches 
            ? 'dark' 
            : 'light';
        this.applyTheme(systemTheme);
        this.updateToggleButton();
    }
}

// Initialize dark mode manager
const darkModeManager = new DarkModeManager();

// Export for global access
window.DarkModeManager = darkModeManager;

// Add to BautagebuchApp namespace if it exists
if (window.BautagebuchApp) {
    window.BautagebuchApp.darkMode = {
        toggle: () => darkModeManager.toggleTheme(),
        setTheme: (theme) => darkModeManager.setTheme(theme),
        getCurrentTheme: () => darkModeManager.getCurrentTheme(),
        resetToSystem: () => darkModeManager.resetToSystemPreference()
    };
}

// Handle theme-specific adjustments for third-party components
window.addEventListener('themeChanged', (e) => {
    const { theme } = e.detail;
    
    // Update any charts or other components that need theme-specific styling
    if (window.Chart) {
        // Update Chart.js default colors if used
        Chart.defaults.color = theme === 'dark' ? '#cbd5e1' : '#374151';
        Chart.defaults.borderColor = theme === 'dark' ? '#334155' : '#e5e7eb';
        Chart.defaults.backgroundColor = theme === 'dark' ? '#1e293b' : '#ffffff';
    }
    
    // Update any other theme-dependent components
    document.dispatchEvent(new CustomEvent('darkModeToggled', { 
        detail: { theme, isDark: theme === 'dark' } 
    }));
});

// Utility function to check if dark mode is active
window.isDarkMode = () => darkModeManager.getCurrentTheme() === 'dark';

// CSS-in-JS for dynamic theme switching (fallback)
const injectThemeStyles = () => {
    const styleId = 'dynamic-theme-styles';
    let styleElement = document.getElementById(styleId);
    
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = styleId;
        document.head.appendChild(styleElement);
    }
    
    // Additional dynamic styles can be added here if needed
    styleElement.textContent = `
        /* Dynamic theme transition improvements */
        .theme-transition * {
            transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease !important;
        }
        
        /* Ensure proper focus styles in both themes */
        [data-theme="dark"] *:focus {
            outline-color: #60a5fa;
        }
        
        /* Improve text selection in dark mode */
        [data-theme="dark"] ::selection {
            background-color: #3b82f6;
            color: #ffffff;
        }
        
        /* Better form styling in dark mode */
        [data-theme="dark"] input[type="text"]:focus,
        [data-theme="dark"] input[type="email"]:focus,
        [data-theme="dark"] input[type="password"]:focus,
        [data-theme="dark"] textarea:focus,
        [data-theme="dark"] select:focus {
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
    `;
};

// Inject additional styles
injectThemeStyles();

// Add smooth transition class to body after initial load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.body.classList.add('theme-transition');
    }, 100);
});
