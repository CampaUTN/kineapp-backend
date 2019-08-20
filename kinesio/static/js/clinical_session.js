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

function close_session() {
    $('#card_session').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_session').remove()
    });
}


$('[data-fancybox="preview"]').fancybox({
  thumbs : {
    autoStart : true
  }
});