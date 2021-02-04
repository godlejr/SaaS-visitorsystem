
$(document).ready(function() {

    $('.rolling-banner').on('init',function() {
        $('.rolling-banner .banner-item').css('display', 'block');
    }).slick({
        dots: false,
        speed: 1000,
        arrows: false,
        autoplay: true,
        nextArrow: false,
        autoplaySpeed: 2500

    });
});