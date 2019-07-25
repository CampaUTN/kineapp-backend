function signOut() {
    $.get('logout/').then(function () {
        location.href = '/';
    });
}

function onSuccess(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;

    //For test purpose
    console.log('google_token: ' + id_token)

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
            } else {
                $('.modal-content').load('no_user/', function(){
                    $('#modalGeneric').modal({show:true});
                });
            }
        },
        error: function(){
            console.log("There was an error. ")
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
