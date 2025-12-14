jQuery(document).ready(function($) {
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
