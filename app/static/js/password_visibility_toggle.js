function togglePasswordVisibility(inputId, toggleId) {
    const jQInput = $(`#${inputId}`);

    if (jQInput.attr("type") === "password") {
        jQInput.attr("type", "text");
        setEyeWithoutSlash(toggleId);
    } else {
        jQInput.attr("type", "password");
        setEyeWithSlash(toggleId);
    }
}

function setEyeWithSlash(toggleId) {
    const jQToggle = $(`#${toggleId}`);
    jQToggle.removeClass("bi-eye");
    jQToggle.addClass("bi-eye-slash");
}

function setEyeWithoutSlash(toggleId) {
    const jQToggle = $(`#${toggleId}`);
    jQToggle.removeClass("bi-eye-slash");
    jQToggle.addClass("bi-eye");
}

$(document).ready(function() {
    $(".toggle-password-visibility").on("click", function(e) {
        const jQToggle = $(e.target);
        togglePasswordVisibility(jQToggle.attr("data-target"), jQToggle.attr("id"));
    });
});
