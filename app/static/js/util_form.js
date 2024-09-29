/**
 * Converts <form> element and its data to a JSON for Ajax.
 */
function formToJSON(formObj) {
    let array = formObj.serializeArray();
    let json = {};
  
    $.map(array, function(n, i) {
        json[n["name"]] = n["value"];
    });
  
    return json;
}

$(document).ready(function() {
    // remove invalid input highlighting and error message when user inputs into field
    $(".form-control").on("input", function() {
        if ($(this).hasClass("is-invalid")) {
            $(this).removeClass("is-invalid");
            $(this).siblings(".invalid-feedback").text("");
        }
    });
});
