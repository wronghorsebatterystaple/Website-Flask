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
    $("#post-content").find("a").addClass("link-customblue");

    $("table").find("p").addClass("mb-0"); // markdown_grid_tables tables generate <p> tags with too much spacing
    $("td").each(function() {
        if ($(this).find("pre").length > 0) {
            $(this).addClass("align-top"); // cells containing code blocks are top-aligned
            $(this).find("pre").addClass("mb-0");
        }
    });

    $(".footnote").first().attr("id", "footnotes");
    $("#footnotes").find("p").addClass("mb-1");
    $("#footnotes").find("a").each(function() {
        if (!$(this).hasClass("footnote-backref")) {
            $(this).attr("target", "_blank");
        }
    });

    genFootnoteTooltips();
});

$(document).on("mouseover", ".footnote-ref", function(e) {
    const callback = (mutationList, observer) => {
        MathJax.typeset([".tooltip"]);
        observer.disconnect();
    };

    // we have to wait for tooltip div to be created to rerender LaTeX
    const observer = new MutationObserver(callback);
    observer.observe(document.body, {subtree: false, childList: true});
});
