$(document).ready(function() {
    $("#what-meow-button").on("mouseenter", function() {
        $("#meow-btn").addClass("invisible");
    });
    $("#what-meow-button").on("mouseleave", function() {
        $("#meow-btn").removeClass("invisible");
    });
});
