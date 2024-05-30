function togglePasswordVisibility(targetId, visToggleId) {
    const target_elem = $(`#${targetId}`);
    if (target_elem.attr("type") == "password") {
        target_elem.attr("type", "text");
    } else {
        target_elem.attr("type", "password");
    }

    $(`#${visToggleId}`).get(0).classList.toggle("bi-eye");
}

$(document).ready(function() {
    $(".password-vis-toggle").on("click", function(e) {
        const visToggle_elem = $(e.target);
        togglePasswordVisibility(visToggle_elem.attr("data-target"), visToggle_elem.attr("id"));
    });
});
