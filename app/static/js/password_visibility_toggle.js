function togglePasswordVisibility(passwordInputId, visToggleId) {
    const passwordInput_elem = $(`#${passwordInputId}`);

    if (passwordInput_elem.attr("type") === "password") {
        passwordInput_elem.attr("type", "text");
        setEyeWithoutSlash(visToggleId);
    } else {
        passwordInput_elem.attr("type", "password");
        setEyeWithSlash(visToggleId);
    }
}

function setEyeWithSlash(visToggleId) {
    const visToggle_elem = $(`#${visToggleId}`);
    visToggle_elem.removeClass("bi-eye");
    visToggle_elem.addClass("bi-eye-slash");
}

function setEyeWithoutSlash(visToggleId) {
    const visToggle_elem = $(`#${visToggleId}`);
    visToggle_elem.removeClass("bi-eye-slash");
    visToggle_elem.addClass("bi-eye");
}

$(document).ready(function() {
    $(".password-vis-toggle").on("click", function(e) {
        const visToggle_elem = $(e.target);
        togglePasswordVisibility(visToggle_elem.attr("data-target"), visToggle_elem.attr("id"));
    });
});
