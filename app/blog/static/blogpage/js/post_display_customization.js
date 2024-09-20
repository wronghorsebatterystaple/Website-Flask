function applyPostAndCommentStyles(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length <= 0) {
        return;
    }
    const jQPostContent = jQBase.find("#post__content");
    const jQCommentContent = jQBase.find(".comment__content");
    const jQPostAndCommentContent = $.merge(jQPostContent, jQCommentContent);

    // make all links except same-page ones indicated by custom markdown and same-page URL fragments
    // (including footnotes and footnote backrefs) open in new tab
    jQPostAndCommentContent.find("a").each(function() {
        if (!$(this).is("[data-same-page]") && !$(this).attr("href").startsWith("#")) {
            $(this).attr("target", "_blank");
        }
    });

    // add CSS classes for extra styling
    jQPostContent.find("h1").addClass("post__h1 ");
    jQCommentContent.find("h1").addClass("comment__h1");
    jQPostContent.find("h2").addClass("post__h2");
    jQCommentContent.find("h2").addClass("comment__h2");
    jQPostContent.find("img").addClass("post__img");
    jQCommentContent.find("img").addClass("comment__img");
    jQPostAndCommentContent.find(".post__h1, .comment__h1")
            .addClass("mb-3 border-bottom--h1 custom-green-deep-dark fs-4");
    jQPostAndCommentContent.find(".post__h2, .comment__h2")
            .addClass("mb-3 border-bottom--h2 custom-orange-deep fs-7");

    // images use alt text as hover text too
    jQPostAndCommentContent.find(".post__img[alt], .comment__img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });
}

// for syntax guide
function addCommentHoverTooltip() {
    $("#leave-a-comment [data-class='tooltip--comment-formatting']").parent().prev()
            .append(" (hover to show formatting options)")
            .attr("data-bs-toggle", "tooltip")
            .attr("data-bs-custom-class", "tooltip--text-align-left")
            .attr("data-bs-html", "true")
            .attr("data-bs-title", `
                <ul class='mb-0'>
                  <li>Markdown
                    <ul>
                      <li>No images, links, or footnotes</li>
                      <li>Tables: GFM, or reStructuredText Grid with line separators</li>
                    </ul>
                  </li>
                  <li>LaTeX (via MathJax)
                    <ul>
                      <li>Escape anything that is also Markdown: <code>\\(</code>, <code>\\)</code>, <code>\\\\</code>, <code>\*</code> etc.</li>
                    </ul>
                  </li>
                  <li>My custom inline Markdown syntax if you can figure it out :3</li>
                </ul>
            `);

    refreshTooltips("#leave-a-comment");
}

applyPostAndCommentStyles("body");
addCommentHoverTooltip();
