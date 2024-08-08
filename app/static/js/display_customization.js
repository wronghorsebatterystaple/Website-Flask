function genFootnoteTooltips() {
    const REMOVE_BACKREF_RE = /<a class=["&quot;]+?footnote-backref[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/g;

    $(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        const domFootnote = document.getElementById($(this).attr("href").replace("#", ""));
        var tooltipContent_HTML = $(domFootnote).find("p").first().html().replace(REMOVE_BACKREF_RE, "");

        // replace serialized MathML HTML with its corresponding original LaTeX
        // to render with MathJax.typeset() on mouseover
        const mathItems = MathJax.startup.document.getMathItemsWithin(domFootnote);
        const matches = tooltipContent_HTML.match(MATCH_MATHJAX_RE);
        if (matches != null) {
            for (var i = 0; i < matches.length; i++) {
                var match = matches[i];
                tooltipContent_HTML = tooltipContent_HTML.replace(match, `\\(${mathItems[i].math}\\)`);
            }
        }

        $(this).attr("data-bs-title", tooltipContent_HTML);
    });

    refreshTooltips();
}

function syntaxHighlightNonTable(selector_root) {
    $(selector_root).find("pre code").each(function() {
        if ($(this).parents("table").length === 0) {
            hljs.highlightElement($(this).get(0));
            $(this).addClass("code-block-outside");
        }
    });
}

function applyCustomMarkdown(selector_root) {
    const elemRoot = $(selector_root);
    if (!elemRoot) {
        return;
    }

    // custom table horizontal and vertical align syntax
    elemRoot.find("[data-align-center]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-center");
    });
    elemRoot.find("[data-align-right]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-end");
    });
    elemRoot.find("[data-align-top]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-top");
    });
    elemRoot.find("[data-align-bottom]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-bottom");
    });

    // custom table column width syntax
    elemRoot.find("[data-col-width]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).attr("width", $(this).attr("data-col-width"));
    });

    // no extra space at the end of custom details/summary, and first line of summary starts inline
    elemRoot.find("details").each(function() {
        $(this).children(".md-details-contents").children().last().addClass("mb-0");
        const elemSummary = $(this).find("summary");
        elemSummary.find("p").first().addClass("d-inline");
        elemSummary.children().last().addClass("mb-0");
    });

    // no extra <p> tags in custom figures/captions
    elemRoot.find("figure").find("p").children("img").unwrap();
}

function applyGlobalStyles(selector_root) {
    const elemRoot = $(selector_root);
    if (!elemRoot) {
        return;
    }

    // tables and non-table code blocks scroll horizontally on overflow
    elemRoot.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    elemRoot.find("pre").each(function() {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(HORIZ_SCOLL_DIV_HTML);
        }
    });

    // inline CSS used by Markdown tables converted to class for CSP
    elemRoot.find("[style='text-align: center;']").removeAttr("style").addClass("text-center");
    elemRoot.find("[style='text-align: right;']").removeAttr("style").addClass("text-end");

    // no extra space at the bottom of table cells
    $.merge(elemRoot.find("th"), elemRoot.find("td")).each(function() {
        $(this).children().last().addClass("mb-0");
    });

    // no extra space between lists and their "heading" text
    $.merge(elemRoot.find("ul"), elemRoot.find("ol")).each(function() {
        $(this).prev("p").addClass("mb-0");
    });

    // footnote tweaks
    const elemFootnotes = elemRoot.find(".footnote").first();
    if (elemFootnotes) {
        elemFootnotes.attr("id", "footnotes");
        elemFootnotes.wrap("<details id=\"footnotes-details\" class=\"footnotes-details\"></details>")
        elemFootnotes.before("<summary class=\"footnotes-details-summary\">Footnotes</summary>");

        elemFootnotes.children("hr").first().addClass("footnote-hr");
        elemFootnotes.find("p").addClass("mb-0");
        const elemFootnotesList = elemFootnotes.children("ol").first();
        elemFootnotesList.addClass("mb-0");
        elemFootnotesList.children("li").addClass("mb-1");

        genFootnoteTooltips();
    }

    // footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    elemRoot.find(".footnote-ref").on("click", function(e) {
        const elemFootnoteDetails = elemRoot.find("#footnotes-details");
        if (!elemFootnoteDetails.is("[open]")) {
            elemFootnoteDetails.attr("open", "");
        }
    });
    
    applyCustomMarkdown(selector_root); // Markdown tweaks round 3
    syntaxHighlightNonTable(selector_root);
}

$(document).ready(function() {
    applyGlobalStyles("body");
});
