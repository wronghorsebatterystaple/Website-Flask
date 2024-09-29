$(document).ready(function() {
    $("input[data-class='btn--back']").on("click", function() {
        window.history.back();
    });

    $("input[data-class='btn--needs-confirm']").on("click", function() {
        return confirm("Mouse aim check");
    });

    $("#btn--meow").on("click", function() {
        customFlash("meow :3");
    });
});
