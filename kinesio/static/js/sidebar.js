
$('#search_list').on("change keyup paste", function(){
    let current_query = $('#search_list').val();
    console.log("holaa");
    let list_data = $("#list_data li")
    if (current_query !== "") {
        list_data.hide();
        list_data.each(function(){
            var current_keyword = $(this).text();
            if (current_keyword.indexOf(current_query) >=0) {
                $(this).show();
            };
        });
    } else {
        list_data.show();
    };
});

function get_clinical_history(id_clinical_history){
    $('.data').load('clinical_history/?id_clinical_history=' + id_clinical_history)
}