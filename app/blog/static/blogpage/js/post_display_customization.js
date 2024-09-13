function applyPostAndCommentStyles(baseSelector) {
    const jQueryBase = $(baseSelector);
    if (jQueryBase.length <= 0) {
        return;
    }
    const jQueryPostContent = jQueryBase.find("#post__content");
    const jQueryCommentContents = jQueryBase.find(".comment-content");
    const jQueryPostAndCommentContents = $.merge(jQueryPostContent, jQueryCommentContents);

    // make all links except same-page ones indicated by custom markdown and same-page URL fragments
    // (including footnotes and footnote backrefs) open in new tab
    jQueryPostAndCommentContents.find("a").each(function() {
        if (!$(this).is("[data-same-page]") && !$(this).attr("href").startsWith("#")) {
            $(this).attr("target", "_blank");
        }
    });

    // add CSS classes for extra styling
    jQueryPostAndCommentContents.find("h1").addClass("post__h1 fs-4");
    jQueryPostAndCommentContents.find("h2").addClass("post__h2 fs-7");
    jQueryPostAndCommentContents.find("img").addClass("post__img");

    // images use alt text as hover text too
    jQueryPostAndCommentContents.find("img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });
}

$(document).ready(function() {
    // add comment hover tooltip for syntax guide
    let text = "";
    $("[data-comment-formatting-tooltip]").first().parent().prev().each(function() {
        text = $(this).text();
        $(this).html("<a id=\"comment-formatting-tooltip\"></a>"); // need `<a>` so tooltip disappears on hover end
    });
    $("#comment-formatting-tooltip")
            .append(`${text} (hover to show formatting options)`)
            .attr("data-bs-toggle", "tooltip")
            .attr("data-bs-custom-class", "tooltip--text-align-left")
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
    refreshTooltips("#leave-a-comment");

    applyPostAndCommentStyles("body");
});
