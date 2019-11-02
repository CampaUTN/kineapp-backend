$(function(){

    $('.list-group a').click(function(e) {
        e.preventDefault();

        $that = $(this);

        $("#list_data").find('a').removeClass('active').removeClass("white-text");
        $("#list_data_shared").find('a').removeClass('active').removeClass("white-text");
        $that.addClass('active').addClass("white-text");

    });

    $('#search_clinical').bind("change keyup paste", function(){
        event.preventDefault();
        let value = $(this).val().toLowerCase();
        $("#list_data li").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});

function get_clinical_history_by_patient(patient_id){
    $('.data').load('clinical_history/?patient_id=' + patient_id, null, function (responseText, textStatus, xhr) {
        if(xhr.status == 401 ){
            $('.modal-content').load('secret_questions/',function(){
                $('#modalGeneric').modal();
            });
        }
    })
}
