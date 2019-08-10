$(function(){

    $('.list-group a').click(function(e) {
        e.preventDefault()

        $that = $(this);

        $that.parent().find('a').removeClass('active');
        $that.addClass('active').addClass("white-text");
    });

    $('#search_clinical').bind("change keyup paste", function(){
        event.preventDefault();
        let value = $(this).val().toLowerCase();
        $("#list_data a").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});

function get_clinical_history(clinical_history_id){
    $('.data').load('clinical_history/?clinical_history_id=' + clinical_history_id)
}

function get_clinical_history_by_patient(patient_id){
    $('.data').load('clinical_history/?patient_id=' + patient_id)
}
