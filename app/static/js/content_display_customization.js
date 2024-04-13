window.addEventListener("load", function() {
    // Make sure \(\) inside custom Markdown \lf{}\elf doesn't get even bigger
    $("mjx-container").each(function() {
        if ($(this).parents(".font-latex").length > 0) {
            $(this).css("font-size", "100%");
        }
    });

    // Make footnote links open in new tab
    $(".footnote").find("a").each(function() {
        $(this).attr("target", "_blank");
    });
});
