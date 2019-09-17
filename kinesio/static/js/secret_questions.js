$(function(){
    $('#answer').on("change keyup paste", function(){
        $('#answer').popover('hide');
        $('#answer_button').popover('hide');
    })
});

function check_answer(){
    let answer_input = $('#answer');
    if (answer_input.val() == "") {
        answer_input.addClass('animated bounce').one("animationend", function () {
            answer_input.removeClass('animated bounce')
        });
        answer_input.popover('show');
    } else {
        let question_id = $('#questionSelector').val();
        let google_token=sessionStorage.google_token;
        $.ajax({
            type: 'POST',
            url: 'api/v1/login/',
            data: {
                'secret_question_id': question_id,
                'google_token': google_token,
                'answer': answer_input.val()
            },
            success: function(response) {
                sessionStorage.setItem('token', response.token);

                $('#modalGeneric').modal('hide');
                $('#logo_index').addClass('animated fadeOutDown').one('animationend', function () {
                    location.reload()
                });
            },
            error: function(response){
                answer_input.addClass('animated bounce');
                let popover= $('#answer_button').popover(
                    {content: response.responseJSON.message}
                );
                $('#answer_button').popover('show');
            },
        });

        return false;
    }
}