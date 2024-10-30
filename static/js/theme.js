class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('themeToggle');
        this.sunIcon = document.querySelector('.sun');
        this.moonIcon = document.querySelector('.moon');
        this.initTheme();
        this.initEventListeners();
    }

    initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
            this.updateIcon(savedTheme === 'dark');
        } else if (prefersDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            this.updateIcon(true);
        }
    }

    updateIcon(isDark) {
        this.themeToggle.checked = isDark;
        this.sunIcon.style.display = isDark ? 'none' : 'block';
        this.moonIcon.style.display = isDark ? 'block' : 'none';
    }

    initEventListeners() {
        this.themeToggle?.addEventListener('change', (e) => {
            const isDark = e.target.checked;
            const theme = isDark ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            this.updateIcon(isDark);
        });

        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    const isDark = e.matches;
                    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
                    this.updateIcon(isDark);
                }
            });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});
