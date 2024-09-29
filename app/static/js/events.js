/* no `$(document).ready()` due to possibility of dynamic content appearing afterwards like post comments */

$(document).on("click", "input[data-class*='btn--back']", function() {
    window.history.back();
});

$(document).on("click", "input[data-class*='btn--needs-confirm']", function() {
    return confirm("Mouse aim check");
});

$(document).ready(function() {
    $("#meow-btn").on("click", function() {
        customFlash("meow :3");
    });
});
