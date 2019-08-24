$(document).ready(function () {
    <!-- Sometimes Google Api charge slow and the button does not render -->
    <!-- This is the solution -->
    renderButton();

});

function signOut() {
    $.get('logout/').then(function () {
        location.href = '/';
    });
}

function onSuccess(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;

    sessionStorage.setItem('google_token', id_token);

    $.ajax({
        type: 'POST',
        url: 'api/v1/user_exists/',
        data: {
            'google_token': id_token
        },
        success: function(response, textStatus, xhr) {
            if(xhr.status == 200 ){
                $('.modal-content').load('secret_questions/',function(){
                    $('#modalGeneric').modal();

                });
            }
        },
        error: function(response){
            if(response.status == 406) {
                $('.modal-content').load('no_user/', function(){
                    $('#modalGeneric').modal({show:true});
                });
            } else {
                console.log("There was an error.")
            }
        }});
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
    $.get('clinical_session/?clinical_session_id=' + clinical_session_id).then(function (data) {
        $('#card_history').append(data).one("animationend", function(){
            $('#card_session').removeClass('animated slideInRight')
        });

    })
}

function close_clinical_history() {
    $('#card_history').addClass('animated slideOutRight').one("animationend", function () {
        $('#card_history').remove()
    });
}

function open_timelapse(tag, patient_id){
    $('#timelapse').remove();

    $.get('timelapse/?tag=' + tag + ";patient_id=" + patient_id).then(function (data) {
        $('#card_history').append(data);
        var fancyGallery = $("#timelapse").find("a");
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
    });
}
