window.addEventListener("load", function() {
    $(".footnote").find("a").each(function() {
        if (!$(this).hasClass("footnote-backref")) {
            $(this).attr("target", "_blank");
        }
    });

    $(".footnote").find("p").addClass("mb-2");

    $("#post-content").find("a").addClass("link-customblue");
});
