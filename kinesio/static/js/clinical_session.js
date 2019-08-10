$(function(){

    $('img').each(function() {
        let img = $(this)
        img.onload
    })
});

$(document).ready(function(){

    $('.multiple-items').slick({
        infinite: true,
        slidesToShow: 3,
        rows: 2,
        prevArrow: $(".prev"),
        nextArrow: $(".next"),
        margin: '5 px'
    });
});

$(document).on('click', '[data-toggle="lightbox"]', function(event) {
    event.preventDefault();
    $(this).ekkoLightbox();
});

function close_session() {
    $('#card_session').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_session').remove()
    });
}

function fullscreen_image(){
    console.log("FULL SCREEN");
}