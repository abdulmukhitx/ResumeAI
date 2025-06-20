/* 
CONSOLE DEBUG COMMANDS FOR THEME TOGGLE
========================================

Copy and paste these commands in your browser console to debug theme toggle issues:

1. Check current theme status:
*/
debugTheme()

/*
2. Force theme toggle setup:
*/
forceThemeToggleSetup()

/*
3. Test theme toggle manually:
*/
testThemeToggle()

/*
4. Check if theme toggle button exists:
*/
console.log('Theme button:', document.getElementById('theme-toggle'))
console.log('Theme icon:', document.getElementById('theme-icon'))

/*
5. Force theme change to dark:
*/
document.documentElement.setAttribute('data-theme', 'dark')
localStorage.setItem('theme', 'dark')

/*
6. Force theme change to light:
*/
document.documentElement.setAttribute('data-theme', 'light')
localStorage.setItem('theme', 'light')

/*
7. Check all CSS files loaded:
*/
Array.from(document.querySelectorAll('link[rel="stylesheet"]')).forEach(link => 
    console.log('CSS:', link.href)
)

/*
8. Force emergency CSS reload:
*/
const emergencyCSS = document.createElement('link')
emergencyCSS.rel = 'stylesheet'
emergencyCSS.href = '/static/css/emergency-visibility-fix.css?v=' + Date.now()
document.head.appendChild(emergencyCSS)

/*
9. Check if button is visible:
*/
const button = document.getElementById('theme-toggle')
if (button) {
    const styles = window.getComputedStyle(button)
    console.log('Button computed styles:', {
        display: styles.display,
        visibility: styles.visibility,
        opacity: styles.opacity,
        width: styles.width,
        height: styles.height,
        zIndex: styles.zIndex
    })
}

/*
10. Force button to be visible:
*/
const btn = document.getElementById('theme-toggle')
if (btn) {
    btn.style.display = 'flex'
    btn.style.visibility = 'visible'
    btn.style.opacity = '1'
    btn.style.background = '#8c43ff'
    btn.style.width = '50px'
    btn.style.height = '50px'
    btn.style.borderRadius = '50%'
    btn.style.border = '2px solid rgba(255,255,255,0.3)'
    btn.style.color = 'white'
    btn.style.fontSize = '1.2rem'
    btn.style.cursor = 'pointer'
    btn.style.zIndex = '99999'
    console.log('✅ Forced button visibility')
}
