function applyGlobalStyles(baseSelector) {
    const elemBase = $(baseSelector);
    if (elemBase.length <= 0) {
        return;
    }

    // tables and non-table code blocks scroll horizontally on overflow
    elemBase.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    elemBase.find("pre").each(function() {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(HORIZ_SCOLL_DIV_HTML);
        }
    });

    // inline CSS used by Markdown tables converted to class for CSP
    elemBase.find("[style='text-align: center;']").removeAttr("style").addClass("text-center");
    elemBase.find("[style='text-align: right;']").removeAttr("style").addClass("text-end");

    // no extra space at the bottom of table cells
    $.merge(elemBase.find("th"), elemBase.find("td")).each(function() {
        $(this).children().last().addClass("mb-0");
    });

    // no extra space between lists and their "heading" text
    $.merge(elemBase.find("ul"), elemBase.find("ol")).each(function() {
        $(this).prev("p").addClass("mb-0");
    });

    // footnote tweaks
    const elemFootnotes = elemBase.find(".footnote").first();
    if (elemFootnotes.length > 0) {
        elemFootnotes.attr("id", "footnotes");
        elemFootnotes.wrap("<details id=\"footnotes-details\" class=\"footnotes-details\"></details>")
        elemFootnotes.before("<summary class=\"footnotes-details-summary\">Footnotes</summary>");

        elemFootnotes.children("hr").first().addClass("footnote-hr");
        elemFootnotes.find("p").addClass("mb-0");
        const elemFootnotesList = elemFootnotes.children("ol").first();
        elemFootnotesList.addClass("mb-0");
        elemFootnotesList.children("li").addClass("mb-1");

        genFootnoteTooltips(baseSelector);
    }

    // footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    elemBase.find(".footnote-ref").on("click", function(e) {
        const elemFootnoteDetails = elemBase.find("#footnotes-details");
        if (!elemFootnoteDetails.is("[open]")) {
            elemFootnoteDetails.attr("open", "");
        }
    });
    
    applyCustomMarkdown(baseSelector); // Markdown tweaks round 3
    syntaxHighlightNonTable(baseSelector);
}

function applyCustomMarkdown(baseSelector) {
    const elemBase = $(baseSelector);
    if (elemBase.length <= 0) {
        return;
    }

    // custom table horizontal and vertical align syntax
    elemBase.find("[data-align-center]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-center");
    });
    elemBase.find("[data-align-right]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-end");
    });
    elemBase.find("[data-align-top]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-top");
    });
    elemBase.find("[data-align-bottom]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-bottom");
    });

    // custom table column width syntax
    elemBase.find("[data-col-width]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).attr("width", $(this).attr("data-col-width"));
    });

    // no extra space at the end of custom details/summary, and first line of summary starts inline
    elemBase.find("details").each(function() {
        $(this).children(".md-details-contents").children().last().addClass("mb-0");
        const elemSummary = $(this).find("summary");
        elemSummary.find("p").first().addClass("d-inline");
        elemSummary.children().last().addClass("mb-0");
    });

    // no extra <p> tags in custom figures/captions
    elemBase.find("figure").find("p").children("img").unwrap();
}

function genFootnoteTooltips(baseSelector) {
    const elemBase = $(baseSelector);
    if (elemBase.length <= 0) {
        return;
    }
    const REMOVE_BACKREF_RE = /<a class=["&quot;]+?footnote-backref[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/g;

    elemBase.find(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        const domFootnote = document.getElementById($(this).attr("href").replace("#", ""));
        let tooltipContents = $(domFootnote).find("p").first().html().replace(REMOVE_BACKREF_RE, "");

        // replace serialized MathML HTML with its corresponding original LaTeX
        // to render with MathJax.typeset() on mouseover
        const mathItems = MathJax.startup.document.getMathItemsWithin(domFootnote);
        const matches = tooltipContents.match(MATCH_MATHJAX_RE);
        if (matches != null) {
            for (let i = 0; i < matches.length; i++) {
                let match = matches[i];
                tooltipContents = tooltipContents.replace(match, `\\(${mathItems[i].math}\\)`);
            }
        }

        $(this).attr("data-bs-title", tooltipContents);
    });

    refreshTooltips(baseSelector);
}

function syntaxHighlightNonTable(baseSelector) {
    $(baseSelector).find("pre code").each(function() {
        if ($(this).parents("table").length === 0) {
            hljs.highlightElement($(this).get(0));
            $(this).addClass("code-block-outside");
        }
    });
}

$(document).ready(function() {
    applyGlobalStyles("body");
});
