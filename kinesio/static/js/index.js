let idleTime = 0;
$(document).ready(function () {

    //Increment the idle time counter every minute.
    let idleInterval = setInterval(timerIncrement, 60000); // 1 minute

    //Zero the idle timer on mouse movement.
    $(this).mousemove(function (e) {
        idleTime = 0;
    });
    $(this).keypress(function (e) {
        idleTime = 0;
    });

    //Disable right-click on all images
    $('body').on("contextmenu",function(e){
        return false;
    });

    $('[data-toggle="popover"]').popover()
});

function timerIncrement() {
    idleTime = idleTime + 1;

    if (idleTime >= 5 && !($("#modalGeneric").data('bs.modal') || {})._isShown) { // 5 minutes
        $('.modal-content').load('continue_session/', function(){
            parent.$.fancybox.close();
            $('#modalGeneric').modal({show:true});
        });
    }
}


function signOut() {
    $.get('logout/').then(function () {
        location.href = '/';
    });
}

showModalLogin = function(response){
    $('#cover-spin').fadeOut(300);
    if(response.status == 401) {
        $('.modal-content').load('secret_questions/', function(){
            $('#modalGeneric').modal({show:true});
        });
    } else if(response.status == 406) {
        $('.modal-content').load('no_user/', function(){
            $('#modalGeneric').modal({show:true});
        });
    } else {
        console.log("There was an error.");
    }
};

function onSuccess(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;

    sessionStorage.setItem('google_token', id_token);
    $('#cover-spin').fadeIn(300);
    $.ajax({
        type: 'POST',
        url: 'api/v1/user_exists/',
        data: {
            'google_token': id_token
        },
        success: function(response, textStatus, xhr) {
            $('#cover-spin').fadeOut(300);
            if(xhr.status == 200 ){
                $('.modal-content').load('secret_questions/',function(){
                    $('#modalGeneric').modal();

                });
            }
        },
        error: showModalLogin
    });
}

function onFailure(error) {
    console.log(error);
}

function renderButton() {
    gapi.signin2.render('my-signin2', {
        'scope': 'profile email openid',
        'width': 200,
        'height': 50,
        'longtitle': false,
        'theme': 'light',
        'onsuccess': onSuccess,
        'onfailure': onFailure
    });
}

function get_session(clinical_session_id) {
    $('#cover-spin').fadeIn(300);
    $('.list-group-item').addClass('disable');
    $.ajax({
        type: 'GET',
        url: 'clinical_session/?clinical_session_id=' + clinical_session_id,
        success: function(response) {
            $('#cover-spin').fadeOut(300);
            if($('#card_history').length > 0) {
                $('#card_history').append(response).one("animationend", function () {
                    $('#card_session').removeClass('animated slideInRight');
                    $('.list-group-item').removeClass('disable');
                });
            } else {
                $('#cover-spin').fadeOut(300);
                $('.data').html(response).one("animationend", function () {
                    $('#card_session').addClass("width")
                    $('#card_session').removeClass('animated slideInRight');
                    $('.list-group-item').removeClass('disable');
                });
            }
        },
        error: showModalLogin
    });
}

function get_videos() {
    $('#cover-spin').fadeIn(300);
    $('.data').load('videos/', null, function (responseText, textStatus, xhr) {
        $('#cover-spin').fadeOut(300);
        if(xhr.status == 401 ){
            $('.modal-content').load('secret_questions/',function(){
                $('#modalGeneric').modal();
            });
        }
    });
}

function get_rutine(patient_id, medic) {
    $('#cover-spin').fadeIn(300);
    if(medic) {
        $.ajax({
            type: 'GET',
            url: 'routine/?patient_id=' + patient_id,
            success: function(response) {
                $('#cover-spin').fadeOut(300);
                $('#card_history').append(response).one($('#card_routine').width('100%')).one("animationend", function () {
                    $('#card_routine').removeClass('animated slideInRight')
                });
            },
            error: showModalLogin
        });
    } else {
        $('.data').load('routine/?patient_id=' + patient_id, null, function (responseText, textStatus, xhr) {
            $('#cover-spin').fadeOut(300);
            $('#card_routine').removeClass('card_routine_medic').addClass('card_routine_patient');
            if(xhr.status == 401 ){
                $('.modal-content').load('secret_questions/',function(){
                    $('#modalGeneric').modal();
                });
            }
        });
    }

}

function close_routine() {
    $('#card_routine').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_routine').remove()
    });
}

function close_clinical_history() {
    $('#card_history').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_history').remove()
    });
}

function open_timelapse(tag, patient_id){
    $('#timelapse').remove();
    $('#cover-spin').fadeIn(300);
    $.ajax({
        type: 'GET',
        url: 'timelapse/?tag=' + tag + "&patient_id=" + patient_id,
        success: function (data) {
            $('#cover-spin').fadeOut(300);
            $('.data').append(data);

            let fancyGallery = $("#timelapse").find("a");
            fancyGallery.attr("rel","gallery").fancybox({
                type: "image",
                loop: true,
                buttons: [
                    "zoom",
                    "slideShow",
                    "close"
                ],
                protect: true,
                transitionDuration: 5000,
                slideShow: {
                    autoStart: true,
                    speed: 10
                },
            });
            fancyGallery.eq(0).click();
        } ,
        error: showModalLogin
    });

}
