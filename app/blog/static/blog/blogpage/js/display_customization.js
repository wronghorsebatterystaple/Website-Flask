$(document).ready(function() {
    // Add comment hover tooltip for syntax guide
    var contentFieldLabel_elem = $("#content-field").find("label").first();
    contentFieldLabel_elem.html(`<a data-bs-toggle=\"tooltip\" data-bs-custom-class="tooltip-text-align-left" data-bs-html=\"true\" data-bs-title=\"<ul class='mb-0'><li>Markdown<ul><li>Supports reStructuredText Grid tables with line separators</li><li>No images or footnotes</li><li>Link syntax will not be rendered; use plain text</li></ul></li><li>LaTeX (via MathJax)<ul><li>Needs escaping: \\\\\\\\(, \\\\\\\\), \\\\\\\\[, \\\\\\\\], \\\\\\\\\\\\\\\\, and anything like \\\\* that may be interpreted as Markdown</li></ul></li></ul>\">${contentFieldLabel_elem.text()} (hover to see formatting options)</a>`)
    refreshTooltips();

    var postContent_elem = $("#post-content");
    // Make all links except footnotes and footnote backrefs open in new tab
    postContent_elem.find("a").each(function() {
        if (!($(this).hasClass("footnote-ref") || $(this).hasClass("footnote-backref"))) {
            $(this).attr("target", "_blank");
        }
    });

    // Markdown tweaks round 3
    postContent_elem.children("h1").addClass("post-h1");
    postContent_elem.children("h2").addClass("post-h2");
    postContent_elem.find("img").addClass("post-img");
    var commentContent_elems = $(".comment-content");
    commentContent_elems.children("h1").addClass("post-h1");
    commentContent_elems.children("h2").addClass("post-h2");
});
