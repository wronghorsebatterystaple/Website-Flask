function togglePasswordVisibility(inputId, toggleId) {
    const jQueryInput = $(`#${inputId}`);

    if (jQueryInput.attr("type") === "password") {
        jQueryInput.attr("type", "text");
        setEyeWithoutSlash(toggleId);
    } else {
        jQueryInput.attr("type", "password");
        setEyeWithSlash(toggleId);
    }
}

function setEyeWithSlash(toggleId) {
    const jQueryToggle = $(`#${toggleId}`);
    jQueryToggle.removeClass("bi-eye");
    jQueryToggle.addClass("bi-eye-slash");
}

function setEyeWithoutSlash(toggleId) {
    const jQueryToggle = $(`#${toggleId}`);
    jQueryToggle.removeClass("bi-eye-slash");
    jQueryToggle.addClass("bi-eye");
}

$(document).ready(function() {
    $(".toggle--password-visibility").on("click", function(e) {
        const jQueryToggle = $(e.target);
        togglePasswordVisibility(jQueryToggle.attr("data-target"), jQueryToggle.attr("id"));
    });
});
