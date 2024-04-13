// Make sure \(\) inside custom Markdown \lf{}\elf doesn't get even bigger
window.addEventListener("load", function() {
    $("mjx-container").each(function() {
        if ($(this).parents(".font-latex").length > 0) {
            $(this).css("font-size", "100%");
        }
    });
});
