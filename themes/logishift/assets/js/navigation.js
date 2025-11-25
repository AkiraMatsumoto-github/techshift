/**
 * File navigation.js.
 *
 * Handles toggling the navigation menu for small screens and enables TAB key
 * navigation support for dropdown menus.
 */
(function () {
    const siteNavigation = document.getElementById('site-navigation');

    // Return early if the navigation doesn't exist.
    if (!siteNavigation) {
        return;
    }

    const button = siteNavigation.getElementsByTagName('button')[0];

    // Return early if the button doesn't exist.
    if ('undefined' === typeof button) {
        return;
    }

    const menu = siteNavigation.getElementsByTagName('ul')[0];

    // Hide menu by default.
    menu.setAttribute('aria-expanded', 'false');

    if ('undefined' === typeof menu) {
        button.style.display = 'none';
        return;
    }

    if (!menu.classList.contains('nav-menu')) {
        menu.classList.add('nav-menu');
    }

    button.addEventListener('click', function () {
        siteNavigation.classList.toggle('toggled');

        if (button.getAttribute('aria-expanded') === 'true') {
            button.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-expanded', 'false');
        } else {
            button.setAttribute('aria-expanded', 'true');
            menu.setAttribute('aria-expanded', 'true');
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', function (event) {
        const isClickInside = siteNavigation.contains(event.target);

        if (!isClickInside && siteNavigation.classList.contains('toggled')) {
            siteNavigation.classList.remove('toggled');
            button.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-expanded', 'false');
        }
    });

})();
