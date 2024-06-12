function genFootnoteTooltips() {
    const REMOVE_BACKREF_RE = /<a class=["&quot;]+?footnote-backref[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/g;

    $(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        const footnote_dom = document.getElementById($(this).attr("href").replace("#", ""));
        var tooltipContent_HTML = $(footnote_dom).find("p").first().html().replace(REMOVE_BACKREF_RE, "");

        // replace serialized MathML HTML with its corresponding original LaTeX
        // to render with MathJax.typeset() on mouseover
        const mathItems = MathJax.startup.document.getMathItemsWithin(footnote_dom);
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

function applyGlobalStyles(root_selector) {
    const root_elem = $(root_selector);
    if (!root_elem) {
        return;
    }

    // Tables' font also shrinks on mobile
    root_elem.find("table").addClass("shrinking-font-15")

    // Tables and non-table code blocks scroll horizontally on overflow
    root_elem.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    root_elem.find("pre").each(function() {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(HORIZ_SCOLL_DIV_HTML);
        }
    });

    // Inline CSS used by Markdown tables converted to class for CSP
    root_elem.find("[style='text-align: center;']").removeAttr("style").addClass("text-center");
    root_elem.find("[style='text-align: right;']").removeAttr("style").addClass("text-end");
    
    // Markdown tweaks round 3
    // Custom table horizontal and vertical align syntax
    root_elem.find("[data-align-center]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-center");
    });
    root_elem.find("[data-align-right]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("text-end");
    });
    root_elem.find("[data-align-top]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-top");
    });
    root_elem.find("[data-align-bottom]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).addClass("align-bottom");
    });

    // Custom table column width syntax
    root_elem.find("[data-col-width]").each(function() {
        $.merge($(this).parents("th"), $(this).parents("td")).attr("width", $(this).attr("data-col-width"));
    });

    // Footnote tweaks
    const footnotes_elem = root_elem.find(".footnote").first();
    if (footnotes_elem) {
        footnotes_elem.attr("id", "footnotes");
        footnotes_elem.wrap("<details id=\"footnotes-details\" class=\"footnotes-details\"></details>")
        footnotes_elem.before("<summary class=\"footnotes-details-summary\">Footnotes</summary>");

        footnotes_elem.children("hr").first().addClass("footnote-hr");
        footnotes_elem.find("p").addClass("mb-0");
        const footnotesList_elem = footnotes_elem.children("ol").first();
        footnotesList_elem.addClass("mb-0");
        footnotesList_elem.children("li").addClass("mb-1");

        genFootnoteTooltips();
    }

    // Footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    root_elem.find(".footnote-ref").on("click", function(e) {
        const footnoteDetails_elem = root_elem.find("#footnotes-details");
        if (!footnoteDetails_elem.attr("open")) {
            console.log("closed");
            footnoteDetails_elem.attr("open", "");
        }
    });

    // No extra space at the bottom of table cells
    $.merge(root_elem.find("th"), root_elem.find("td")).each(function() {
        $(this).children().last().addClass("mb-0");
    });

    // No extra space between lists and their "heading" text
    $.merge(root_elem.find("ul"), root_elem.find("ol")).each(function() {
        $(this).prev("p").addClass("mb-0"); // no spacing between lists and their "heading" text
    });

    // No extra spaces at the bottom of details/sumary and first line of summary starts inline
    root_elem.find("details").each(function() {
        $(this).children(".md-details-contents").children().last().addClass("mb-0");
        const summary_elem = $(this).find("summary");
        summary_elem.find("p").first().addClass("d-inline");
        summary_elem.children().last().addClass("mb-0");
    });
}

$(document).ready(function() {
    applyGlobalStyles("body");
});
