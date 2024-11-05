function applyPostAndCommentStyles(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length === 0) {
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
    jQPostAndCommentContent.find(".post__h1, .comment__h1").addClass("mb-3 border-bottom--h1 fs-4");
    jQPostAndCommentContent.find(".post__h2, .comment__h2").addClass("mb-3 border-bottom--h2 fs-7");

    // images use alt text as hover text too
    jQPostAndCommentContent.find(".post__img[alt], .comment__img[alt]").each(function() {
        $(this).attr("title", $(this).attr("alt"));
    });
}

// for syntax guide
function addCommentHoverTooltip() {
    $("#leave-a-comment #content-field label").first()
            .append(" (hover to show formatting options)")
            .attr("data-bs-toggle", "tooltip")
            .attr("data-bs-custom-class", "tooltip-text-align-left")
            .attr("data-bs-html", "true")
            .attr("data-bs-title", `
                <ul class='mb-0'>
                  <li>Markdown
                    <ul>
                      <li>Python-Markdown's <code>extra</code> extension is supported</li>
                      <li>No images, links, or footnotes</li>
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

function tweakFootnotes() {
    // turn footnotes into `<details>`
    const jQFootnotes = $("#post__content").find(".footnote");
    if (jQFootnotes.length > 0) {
        // just because the singular form bothers me
        jQFootnotes.addClass("footnotes");
        jQFootnotes.removeClass("footnote");
        jQFootnotes.wrap("<details id=\"footnotes__details\" class=\"footnotes__details\"></details>")
        jQFootnotes.before("<summary class=\"footnotes__details-summary\">Footnotes</summary>");
    }

    // footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    $(".footnote-ref").on("click", function(e) {
        const jQFootnotesDetails = $("#footnotes__details");
        if (!jQFootnotesDetails.is("[open]")) {
            jQFootnotesDetails.attr("open", "");
        }
    });
}

applyPostAndCommentStyles("body");
addCommentHoverTooltip();
tweakFootnotes();
