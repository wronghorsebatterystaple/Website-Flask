// Set CSS class to display asterisk next to required fields' labels.
function asteriskRequiredFields() {
    $("[required]").each(function() {
        if (!$(this).is("[type=\"radio\"]")) {
            $(this).siblings("label").addClass("required-label");
            $(this).parent().siblings("label").addClass("required-label");
        } else {
            $(this).parent().siblings("label").addClass("required-label");
        }
    });
}

window.addEventListener("load", asteriskRequiredFields, false);

// Remove invalid input highlighting and error message when user inputs into field.
$(document).on("input", ".form-control", function() {
    if ($(this).hasClass("is-invalid")) {
        $(this).removeClass("is-invalid");
        $(this).siblings(".invalid-feedback").text("");
    }
});

// Convert <form> element and its data to a JSON for Ajax.
function formToJSON(formObj) {
    var array = formObj.serializeArray();
    var json = {};
  
    $.map(array, function(n, i) {
        json[n["name"]] = n["value"];
    });
  
    return json;
}
