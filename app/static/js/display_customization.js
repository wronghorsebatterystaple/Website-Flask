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
    // mark \[\] LaTeX blocks with identifying class
    $("mjx-math[style='margin-left: 0px; margin-right: 0px;']").addClass("mjx-center");

    // tables, \[\] LaTeX blocks, and non-table code blocks scroll horizontally on overflow
    const divHTML = "<div class=\"scroll-overflow-x\"></div>";
    $("table").wrap(divHTML);
    $(".mjx-center").wrap(divHTML);
    $("pre").each(function(e) {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(divHTML);
        }
    });

//    // tables containing only code blocks in at least one row have equal width cols (scuffed)
//    var rowAllCodeBlocks = true;
//    $("table").each(function() {
//        $(this).find("tr").each(function() {
//            rowAllCodeBlocks = true;
//            $(this).find("td").each(function() {
//                if ($(this).find("pre").length === 0) {
//                    rowAllCodeBlocks = false;
//                    return false;
//                }
//            });
//            if (rowAllCodeBlocks) {
//                return false;
//            }
//        });
//
//        if (rowAllCodeBlocks) {
//            $(this).addClass("fixed-table-layout");
//        }
//    });

    // table cells containing code blocks are top-aligned
    $("td").each(function() {
        if ($(this).find("pre").length > 0) {
            $(this).addClass("align-top");
            $(this).find("pre").addClass("mb-0");
        }
    });

    // other Markdown tweaks
    $(".footnote").first().attr("id", "footnotes");
    $("#footnotes").find("p").addClass("mb-1");
    $("#footnotes").find("a").each(function() {
        if (!$(this).hasClass("footnote-backref")) {
            $(this).attr("target", "_blank");
        }
    });

    genFootnoteTooltips();
});

// Rerender LaTeX in tooltips on show
$(document).on("inserted.bs.tooltip",  function(e) {
    MathJax.typeset([".tooltip"]);
});
