// Main JavaScript file for portfolio

$(document).ready(function () {
    // Auto-close alerts after 5 seconds
    setTimeout(function () {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add smooth scrolling to all links
    $("a").on('click', function (event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800);
        }
    });

    // Navbar active state
    var currentUrl = window.location.pathname;
    $('.nav-link').each(function () {
        if ($(this).attr('href') === currentUrl) {
            $(this).addClass('active');
        }
    });

    // Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});
$('#themeToggle').click(function () {
    $('body').toggleClass('light-mode');
    $('.navbar').toggleClass('navbar-dark navbar-light');
    $(this).find('i').toggleClass('fa-moon fa-sun');
});