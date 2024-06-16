function applyCommentStyles() {
    var commentContent_elems = $(".comment-content");
    commentContent_elems.find("h1").addClass("post-h1");
    commentContent_elems.find("h2").addClass("post-h2");
}

$(document).ready(function() {
    // Add comment hover tooltip for syntax guide
    var contentFieldLabel_elem = $("#content-field").find("label").first();
    contentFieldLabel_elem.html(`<a data-bs-toggle=\"tooltip\" data-bs-custom-class="tooltip-text-align-left" data-bs-html=\"true\" data-bs-title=\"<ul class='mb-0'><li>Markdown<ul><li>Tables: GFM, or reStructuredText Grid with line separators</li><li>No images</li><li>Links are not rendered; use plain text & no footnotes</li></ul></li><li>LaTeX (via MathJax)<ul><li>Needs escaping: \\\\\\\\(, \\\\\\\\), \\\\\\\\[, \\\\\\\\], \\\\\\\\\\\\\\\\, and anything like \\\\* that may be interpreted as Markdown</li></ul></li><li>My custom inline Markdown syntax if you can figure it out :]</li></ul>\">${contentFieldLabel_elem.text()} (hover to see formatting options)</a>`)
    refreshTooltips();

    var postContent_elem = $("#post-content");
    // Make all links except footnotes and footnote backrefs open in new tab
    postContent_elem.find("a").each(function() {
        if (!$(this).hasClass("footnote-ref") && !$(this).hasClass("footnote-backref")
                && !$(this).attr("href").startsWith("#") && !$(this).is("[data-same-page]")) {
            $(this).attr("target", "_blank");
        }
    });

    // Markdown tweaks round 3
    var h1_headingId = 0;
    var h2_headingId = 0;
    postContent_elem.find("h1").each(function() {
        $(this).addClass("post-h1");
        $(this).attr("id", "h1-" + h1_headingId); // allow linking
        h1_headingId++;
    });
    postContent_elem.find("h2").each(function() {
        $(this).addClass("post-h2");
        $(this).attr("id", "h2-" + h2_headingId);
        h2_headingId++;
    });
    postContent_elem.find("img").addClass("post-img");

    // Images in posts use alt text as hover text too
    postContent_elem.find("img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });

    applyCommentStyles();
});
