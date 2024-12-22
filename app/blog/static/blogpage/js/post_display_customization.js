function applyPostAndCommentStyles(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length === 0) {
        return;
    }
    const jQPostContent = jQBase.find("#post__content");
    const jQCommentContent = jQBase.find(".comment__content");
    const jQPostAndCommentContent = $.merge(jQPostContent, jQCommentContent);

    // add CSS classes for extra styling
    jQPostContent.find("h1").addClass("post__h1 ");
    jQCommentContent.find("h1").addClass("comment__h1");
    jQPostContent.find("h2").addClass("post__h2");
    jQCommentContent.find("h2").addClass("comment__h2");
    jQPostContent.find("img").addClass("post__img");
    jQCommentContent.find("img").addClass("comment__img");
    jQPostAndCommentContent.find(".post__h1, .comment__h1").addClass("mb-3 border-bottom--h1 fs-4");
    jQPostAndCommentContent.find(".post__h2, .comment__h2").addClass("mb-3 border-bottom--h2 fs-7");

    // default open certain dropdowns in post
    jQBase.find("details").filter(".md-dropdown-ex, .md-dropdown-notat").attr("open", "");
}

// for syntax guide
function addCommentHoverTooltip() {
    $("#leave-a-comment #content-field label").first()
            .append(" (hover to show formatting options)")
            .attr("data-bs-toggle", "tooltip")
            .attr("data-bs-custom-class", "comment-tooltip")
            .attr("data-bs-html", "true")
            .attr("data-bs-title",
                    "Markdown:" +
                      "<ul>" +
                        "<li>Python-Markdown with <code>extra</code> extension</li>" +
                        "<li>No images, links, or footnotes</li>" +
                      "</ul>" +
                    "LaTeX (MathJax):" +
                      "<ul>" +
                        "<li>Escape anything that is also Markdown: <code>\\(</code>, <code>\\)</code>," +
                                "<code>\\\\</code>, <code>\*</code> etc.</li>" +
                        "<li>My custom commands are available if you can find them :3" +
                      "</ul>");

    refreshTooltips("#leave-a-comment");
}

function tweakFootnotes() {
    // turn footnotes into `<details>`
    const jQFootnotes = $("#post__content").find(".footnote");
    if (jQFootnotes.length > 0) {
        // just because the singular form bothers me
        jQFootnotes.addClass("footnotes");
        jQFootnotes.removeClass("footnote");
        jQFootnotes.wrap('<details id="footnotes__wrapper" class="footnotes__wrapper"></details>')
        jQFootnotes.before("<summary>Footnotes</summary>");
    }

    // footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    $(".footnote-ref").on("click", function() {
        $("#footnotes__wrapper").attr("open", "");
    });
}

applyPostAndCommentStyles("body");
addCommentHoverTooltip();
tweakFootnotes();
// for making sure TOC is vertically centered
document.documentElement.style.setProperty("--toc-heading-outer-height", `${$("#toc__heading").outerHeight()}px`);
