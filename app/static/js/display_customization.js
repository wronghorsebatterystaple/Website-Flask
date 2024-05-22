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

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

$(document).ready(function() {
    // Mark \[\] LaTeX blocks with identifying class and make their font shrink on mobile
    $("mjx-math[style='margin-left: 0px; margin-right: 0px;']").addClass("mjx-center shrinking-font");

    // Tables' font also shrinks on mobile
    $("table").addClass("shrinking-font")

    // Tables, \[\] LaTeX blocks, and non-table code blocks scroll horizontally on overflow
    const divHTML = "<div class=\"scroll-overflow-x\"></div>";
    $("table").wrap(divHTML);
    $(".mjx-center").wrap(divHTML);
    $("pre").each(function(e) {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(divHTML);
        }
    });

    // Inline CSS used by Markdown tables converted to class for CSP
    $("[style='text-align: center;']").removeAttr("style").addClass("text-center");
    $("[style='text-align: right;']").removeAttr("style").addClass("text-end");

    // Markdown tweaks round 3
    $("details").find("p").contents().unwrap();
    $("table").find("p").contents().unwrap();

    // Custom table column width syntax
    $("[data-col-width]").each(function() {
        $(this).parents("td").attr("width", $(this).attr("data-col-width"));
        $(this).parents("th").attr("width", $(this).attr("data-col-width"));
    });

    // Custom table horizontal and vertical align syntax
    $("[data-align-center]").each(function() {
        $(this).parents("td").addClass("text-center");
        $(this).parents("th").addClass("text-center");
    });
    $("[data-align-right]").each(function() {
        $(this).parents("td").addClass("text-end");
        $(this).parents("th").addClass("text-end");
    });
    $("[data-align-top]").each(function() {
        $(this).parents("td").addClass("align-top");
        $(this).parents("th").addClass("align-top");
    });
    $("[data-align-bottom]").each(function() {
        $(this).parents("td").addClass("align-bottom");
        $(this).parents("th").addClass("align-bottom");
    });

    var footnotes_elem = $(".footnote").first();
    footnotes_elem.attr("id", "footnotes");
    footnotes_elem.find("p").addClass("mb-1");
    footnotes_elem.find("a").each(function() {
        if (!$(this).hasClass("footnote-backref")) {
            $(this).attr("target", "_blank");
        }
    });
    footnotes_elem.wrap("<details id=\"footnotes-details\" class=\"footnotes-details\"></details>")
    footnotes_elem.before("<summary class=\"footnotes-details-summary\">Footnotes</summary>");
    footnotes_elem.children("hr").first().addClass("footnote-hr");
    footnotes_elem.children("ol").first().addClass("mb-0");
    genFootnoteTooltips();

    // Footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    $(".footnote-ref").on("click", function(e) {
        var footnoteDetails_elem = $("#footnotes-details");
        if (!footnoteDetails_elem.attr("open")) {
            footnoteDetails_elem.attr("open", "");
        }
    });
});

// Rerender LaTeX in tooltips on show
$(document).on("inserted.bs.tooltip",  function(e) {
    MathJax.typeset([".tooltip"]);
});
