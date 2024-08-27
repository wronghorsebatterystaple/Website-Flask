function togglePasswordVisibility(passwordInputId, visToggleId) {
    const elemPasswordInput = $(`#${passwordInputId}`);

    if (elemPasswordInput.attr("type") === "password") {
        elemPasswordInput.attr("type", "text");
        setEyeWithoutSlash(visToggleId);
    } else {
        elemPasswordInput.attr("type", "password");
        setEyeWithSlash(visToggleId);
    }
}

function setEyeWithSlash(visToggleId) {
    const elemVisToggle = $(`#${visToggleId}`);
    elemVisToggle.removeClass("bi-eye");
    elemVisToggle.addClass("bi-eye-slash");
}

function setEyeWithoutSlash(visToggleId) {
    const elemVisToggle = $(`#${visToggleId}`);
    elemVisToggle.removeClass("bi-eye-slash");
    elemVisToggle.addClass("bi-eye");
}

$(document).ready(function() {
    $(".password-visibility-toggle").on("click", function(e) {
        const elemVisToggle = $(e.target);
        togglePasswordVisibility(elemVisToggle.attr("data-target"), elemVisToggle.attr("id"));
    });
});
