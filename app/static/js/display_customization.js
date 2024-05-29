function genFootnoteTooltips() {
    const REMOVE_BACKREF_RE = /<a class=["&quot;]+?footnote-backref[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/g;

    $(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        var footnote_dom = document.getElementById($(this).attr("href").replace("#", ""));
        var footnote_html = $(footnote_dom).find("p").html().replace(REMOVE_BACKREF_RE, "");
        
        // replace serialized MathML HTML with its corresponding original LaTeX
        // to render with MathJax.typeset() on mouseover
        const mathItems = MathJax.startup.document.getMathItemsWithin(footnote_dom);
        const matches = footnote_html.match(MATCH_MATHJAX_RE);
        if (matches != null) {
            for (var i = 0; i < matches.length; i++) {
                var match = matches[i];
                footnote_html = footnote_html.replace(match, `\\(${mathItems[i].math}\\)`);
            }
        }

        $(this).attr("data-bs-title", footnote_html);
    });

    refreshTooltips();
}

function applyGlobalStyles(root_selector) {
    const root_elem = $(root_selector);
    if (!root_elem) {
        return;
    }

    // Make font of \[\] LaTeX blocks shrink on mobile and make them scroll horizontally on overflow
    const HORIZ_SCOLL_DIV_HTML = "<div class=\"scroll-overflow-x\"></div>";
    const HORIZ_SCOLL_DIV_HTML_WIDTH_FULL = "<div class=\"scroll-overflow-x\" width=\"full\"></div>";
    root_elem.find("mjx-math[style='margin-left: 0px; margin-right: 0px;']").addClass("shrinking-font-15").wrap(HORIZ_SCOLL_DIV_HTML);
    root_elem.find("mjx-math[width='full']").addClass("shrinking-font-15").wrap(HORIZ_SCOLL_DIV_HTML_WIDTH_FULL); // for \tag{}ed

    // Tables' font also shrinks on mobile
    root_elem.find("table").addClass("shrinking-font-15")

    // Tables and non-table code blocks scroll horizontally on overflow
    root_elem.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    root_elem.find("pre").each(function(e) {
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

    $.merge(root_elem.find("th"), root_elem.find("td")).each(function() {
        $(this).find("p").last().addClass("mb-0");
    });
    root_elem.find("details").each(function() {
        var summaryParagraphs_elem = $(this).find("summary").find("p");
        if (summaryParagraphs_elem) {
            summaryParagraphs_elem.first().addClass("d-inline");
            summaryParagraphs_elem.last().addClass("mb-0");
        }
        $(this).find("p").last().addClass("mb-0");
    });

    var footnotes_elem = root_elem.find(".footnote").first();
    if (footnotes_elem) {
        footnotes_elem.attr("id", "footnotes");
        footnotes_elem.find("p").addClass("mb-1");
        footnotes_elem.wrap("<details id=\"footnotes-details\" class=\"footnotes-details\"></details>")
        footnotes_elem.before("<summary class=\"footnotes-details-summary\">Footnotes</summary>");
        footnotes_elem.children("hr").first().addClass("footnote-hr");
        footnotes_elem.children("ol").first().addClass("mb-0");
        genFootnoteTooltips();
    }

    // Footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    root_elem.find(".footnote-ref").on("click", function(e) {
        var footnoteDetails_elem = root_elem.find("#footnotes-details");
        if (!footnoteDetails_elem.attr("open")) {
            footnoteDetails_elem.attr("open", "");
        }
    });
}

$(document).ready(function() {
    applyGlobalStyles("body");
});
