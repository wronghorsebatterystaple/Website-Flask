function togglePasswordVisibility(passwordInputId, visToggleId) {
    const jQueryPasswordInput = $(`#${passwordInputId}`);

    if (jQueryPasswordInput.attr("type") === "password") {
        jQueryPasswordInput.attr("type", "text");
        setEyeWithoutSlash(visToggleId);
    } else {
        jQueryPasswordInput.attr("type", "password");
        setEyeWithSlash(visToggleId);
    }
}

function setEyeWithSlash(visToggleId) {
    const jQueryVisToggle = $(`#${visToggleId}`);
    jQueryVisToggle.removeClass("bi-eye");
    jQueryVisToggle.addClass("bi-eye-slash");
}

function setEyeWithoutSlash(visToggleId) {
    const jQueryVisToggle = $(`#${visToggleId}`);
    jQueryVisToggle.removeClass("bi-eye-slash");
    jQueryVisToggle.addClass("bi-eye");
}

$(document).ready(function() {
    $(".toggle--password-visibility").on("click", function(e) {
        const jQueryVisToggle = $(e.target);
        togglePasswordVisibility(jQueryVisToggle.attr("data-target"), jQueryVisToggle.attr("id"));
    });
});
