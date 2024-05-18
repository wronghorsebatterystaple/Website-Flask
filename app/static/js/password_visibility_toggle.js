function togglePasswordVisibility(targetId, visToggleId) {
    var target_elem = $(`#${targetId}`);
    if (target_elem.attr("type") == "password") {
        target_elem.attr("type", "text");
    } else {
        target_elem.attr("type", "password");
    }

    $(`#${visToggleId}`).get(0).classList.toggle("bi-eye");
}

$(document).ready(function() {
    $(".password-vis-toggle").on("click", function(e) {
        var visToggle_elem = $(e.target);
        togglePasswordVisibility(visToggle_elem.attr("data-target"), visToggle_elem.attr("id"));
    });
});
