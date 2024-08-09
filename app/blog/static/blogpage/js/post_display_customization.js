function applyCommentStyles() {
    const elemCommentContents = $(".comment-content");

    // add CSS classes for extra styling
    elemCommentContents.find("h1").addClass("post-h1");
    elemCommentContents.find("h2").addClass("post-h2");
}

/**
 * Replaces whitespace with hyphens and removes all non-alphanumeric and non-hyphen characters.
 */
function sanitizeHeadingForURL(heading) {
    heading = heading.split(/\s+/).join("-");
    return heading.replace(/[^A-Za-z0-9-]/g, "");
}

$(document).ready(function() {
    const elemPostContent = $("#post-content");

    // make all links except footnotes and footnote backrefs open in new tab
    elemPostContent.find("a").each(function() {
        if (!$(this).hasClass("footnote-ref") && !$(this).hasClass("footnote-backref")
                && !$(this).attr("href").startsWith("#") && !$(this).is("[data-same-page]")) {
            $(this).attr("target", "_blank");
        }
    });

    // add CSS classes for extra styling
    elemPostContent.find("h1").addClass("post-h1");
    elemPostContent.find("h2").addClass("post-h2");
    // allows linking via URL fragments
    $.merge($(".post-h1"), $(".post-h2")).each(function() {
        $(this).attr("id", sanitizeHeadingForURL($(this).text()));
    });
    elemPostContent.find("img").addClass("post-img");

    // images in posts use alt text as hover text too
    elemPostContent.find("img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });

    // add comment hover tooltip for syntax guide
    let text = "";
    $("[data-comment-formatting-tooltip]").first().parent().prev().each(function() {
        text = $(this).text();
        $(this).html("<a id=\"comment-formatting-tooltip\"></a>"); // need `<a>` so tooltip disappears on hover end
    });
    $("#comment-formatting-tooltip")
            .append(`${text} (hover to show formatting options)`)
            .attr("data-bs-toggle", "tooltip")
            .attr("data-bs-custom-class", "tooltip-text-align-left")
            .attr("data-bs-html", "true")
            .attr("data-bs-title", `
                <ul class='mb-0'>
                  <li>Markdown
                    <ul>
                      <li>Tables: GFM, or reStructuredText Grid with line separators</li>
                      <li>No images</li>
                      <li>Links are not rendered; use plain text & no footnotes</li>
                    </ul>
                  </li>
                  <li>LaTeX (via MathJax)
                    <ul>
                      <li>Needs escaping: \\\\\\\\(, \\\\\\\\), \\\\\\\\[, \\\\\\\\], \\\\\\\\\\\\\\\\, and anything like \\\\* that may be interpreted as Markdown</li>
                    </ul>
                  </li>
                  <li>My custom inline Markdown syntax if you can figure it out :3</li>
                </ul>
            `);
    refreshTooltips();

    applyCommentStyles();
});
