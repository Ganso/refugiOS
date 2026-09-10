function switchLanguage(lang) {
    var viewEs = document.getElementById('view-es');
    var viewEn = document.getElementById('view-en');
    var btnEs = document.getElementById('btn-es');
    var btnEn = document.getElementById('btn-en');
    var navDl = document.querySelector('.nav-dl-text');
    var footerLogo = document.getElementById('footer-logo-text');
    var footerLicense = document.getElementById('footer-license-text');

    if (lang === 'en') {
        if (viewEs) viewEs.classList.remove('active-view');
        if (viewEn) viewEn.classList.add('active-view');
        if (btnEs) btnEs.classList.remove('active');
        if (btnEn) btnEn.classList.add('active');
        if (navDl) navDl.textContent = 'Downloads';
        if (footerLogo) footerLogo.textContent = 'Logo and visual identity by';
        if (footerLicense) footerLicense.textContent = 'Free software under license';
        document.documentElement.lang = 'en';
        try { localStorage.setItem('refugios_lang', 'en'); } catch(e) {}
    } else {
        if (viewEn) viewEn.classList.remove('active-view');
        if (viewEs) viewEs.classList.add('active-view');
        if (btnEn) btnEn.classList.remove('active');
        if (btnEs) btnEs.classList.add('active');
        if (navDl) navDl.textContent = 'Descargas';
        if (footerLogo) footerLogo.textContent = 'Logotipo e identidad visual por';
        if (footerLicense) footerLicense.textContent = 'Software libre bajo licencia';
        document.documentElement.lang = 'es';
        try { localStorage.setItem('refugios_lang', 'es'); } catch(e) {}
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var btnEs = document.getElementById('btn-es');
    var btnEn = document.getElementById('btn-en');
    var bannerBtnEn = document.getElementById('banner-btn-en');
    var bannerBtnEs = document.getElementById('banner-btn-es');

    if (btnEs) {
        btnEs.addEventListener('click', function() { switchLanguage('es'); });
    }
    if (btnEn) {
        btnEn.addEventListener('click', function() { switchLanguage('en'); });
    }
    if (bannerBtnEn) {
        bannerBtnEn.addEventListener('click', function() { switchLanguage('en'); });
    }
    if (bannerBtnEs) {
        bannerBtnEs.addEventListener('click', function() { switchLanguage('es'); });
    }

    var saved = null;
    try { saved = localStorage.getItem('refugios_lang'); } catch(e) {}
    if (saved === 'en' || saved === 'es') {
        switchLanguage(saved);
    } else {
        var navLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
        if (navLang.startsWith('en')) {
            switchLanguage('en');
        } else {
            switchLanguage('es');
        }
    }
});
