function confirmBtn(btnHandler) {
    return function() {
        if (!confirm("Mouse aim check")) {
            return false;
        }
        btnHandler.apply(this, arguments);
    };
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
