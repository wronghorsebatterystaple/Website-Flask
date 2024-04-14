window.addEventListener("load", function() {
    $(".footnote").first().attr("id", "footnotes");
    $("#footnotes").find("p").addClass("mb-2");
    $("#footnotes").find("a").each(function() {
        if (!$(this).hasClass("footnote-backref")) {
            $(this).attr("target", "_blank");
        }
    });

    $("#post-content").find("a").addClass("link-customblue");
});
