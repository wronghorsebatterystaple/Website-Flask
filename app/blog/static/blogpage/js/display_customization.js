function applyCommentStyles() {
    const elemCommentContents = $(".comment-content");

    // add CSS classes for extra styling
    elemCommentContents.find("h1").addClass("post-h1");
    elemCommentContents.find("h2").addClass("post-h2");
}

$(document).ready(function() {
    // add comment hover tooltip for syntax guide
    var elemContentFieldLabel = $("#content-field").find("label").first();
    elemContentFieldLabel.html(`<a data-bs-toggle=\"tooltip\" data-bs-custom-class="tooltip-text-align-left" data-bs-html=\"true\" data-bs-title=\"<ul class='mb-0'><li>Markdown<ul><li>Tables: GFM, or reStructuredText Grid with line separators</li><li>No images</li><li>Links are not rendered; use plain text & no footnotes</li></ul></li><li>LaTeX (via MathJax)<ul><li>Needs escaping: \\\\\\\\(, \\\\\\\\), \\\\\\\\[, \\\\\\\\], \\\\\\\\\\\\\\\\, and anything like \\\\* that may be interpreted as Markdown</li></ul></li><li>My custom inline Markdown syntax if you can figure it out :3</li></ul>\">${elemContentFieldLabel.text()} (hover to see formatting options)</a>`)
    refreshTooltips();

    var elemPostContent = $("#post-content");
    // make all links except footnotes and footnote backrefs open in new tab
    elemPostContent.find("a").each(function() {
        if (!$(this).hasClass("footnote-ref") && !$(this).hasClass("footnote-backref")
                && !$(this).attr("href").startsWith("#") && !$(this).is("[data-same-page]")) {
            $(this).attr("target", "_blank");
        }
    });

    // add CSS classes for extra styling
    var h1_headingId = 0;
    var h2_headingId = 0;
    elemPostContent.find("h1").each(function() {
        $(this).addClass("post-h1");
        $(this).attr("id", "h1-" + h1_headingId); // allow linking via URL fragments
        h1_headingId++;
    });
    elemPostContent.find("h2").each(function() {
        $(this).addClass("post-h2");
        $(this).attr("id", "h2-" + h2_headingId);
        h2_headingId++;
    });
    elemPostContent.find("img").addClass("post-img");

    // images in posts use alt text as hover text too
    elemPostContent.find("img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });

    applyCommentStyles();
});
