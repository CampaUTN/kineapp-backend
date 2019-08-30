$(document).ready(function(){
    $('.multiple-items').slick({
        infinite: true,
        slidesToShow: 1,
        rows: 1,
        prevArrow: $(".prev"),
        nextArrow: $(".next"),
        margin: '5 px'
    });
});

function close_videos() {
    $('#card_videos').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_videos').remove()
    });
}