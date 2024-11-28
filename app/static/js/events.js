/* no `$(document).ready()` if there's a possibility of dynamic content appearing afterwards, like post comments */

$(document).on("click", "input[data-class*='back-btn']", function() {
    window.history.back();
});

$(document).ready(function() {
    $("#meow-btn").on("click", function() {
        customFlash("meow :3");
    });
});
