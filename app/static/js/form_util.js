// Remove invalid input highlighting and error message when user inputs into field.
$(document).on("input", ".form-control", function() {
    if ($(this).hasClass("is-invalid")) {
        $(this).removeClass("is-invalid"); // this also hides the .invalid-feedback child div I think
        $(this).siblings(".invalid-feedback").text("");
    }
});

// Util function that converts <form> element and its data to a JSON for Ajax.
function formToJSON(formObj) {
    var array = formObj.serializeArray();
    var json = {};
  
    $.map(array, function(n, i) {
        json[n["name"]] = n["value"];
    });
  
    return json;
}
