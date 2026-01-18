jQuery(document).ready(function ($) {
    if ($('.hero-slider-container').length) {
        const heroSwiper = new Swiper('.hero-slider-container', {
            // Optional parameters
            direction: 'horizontal',
            loop: true,
            effect: 'fade', // Sophisticated fade effect
            speed: 1000,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },

            // If we need pagination
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },

            // Navigation arrows
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Theme Tabs Logic
    const themeTabs = document.querySelectorAll('.theme-tabs .region-tab');
    const themeBlocks = document.querySelectorAll('.theme-tag-block');

    themeTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const selectedTheme = this.getAttribute('data-theme');

            // Switch Tabs
            themeTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Switch Content
            themeBlocks.forEach(block => {
                if (block.id === 'theme-block-' + selectedTheme) {
                    block.style.display = 'block';
                } else {
                    block.style.display = 'none';
                }
            });
        });
    });

    // Industry Tabs Logic
    const industryTabs = document.querySelectorAll('.industry-tabs .region-tab');
    const industryBlocks = document.querySelectorAll('.industry-tag-block');

    industryTabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const selectedIndustry = this.getAttribute('data-industry');

            // Switch Tabs
            industryTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // Switch Content
            industryBlocks.forEach(block => {
                if (block.id === 'industry-block-' + selectedIndustry) {
                    block.style.display = 'block';
                } else {
                    block.style.display = 'none';
                }
            });
        });
    });
});
