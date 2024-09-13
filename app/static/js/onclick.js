$(document).ready(function() {
    $("input[data-back-btn][type='submit']").on("click", function() {
        window.history.back();
    });

    $("input[data-confirm-submit][type='submit']").on("click", function() {
        return confirm("Mouse aim check");
    });

    $("#meow").on("click", function() {
        customFlash("meow :3");
    });
});
