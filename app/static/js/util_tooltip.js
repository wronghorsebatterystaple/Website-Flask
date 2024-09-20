function refreshTooltips(baseSelector) {
    const nodeBase = document.querySelector(baseSelector);
    if (!nodeBase) {
        return;
    }

    const tooltipTriggerList = nodeBase.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

function genFootnoteTooltips(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length <= 0) {
        return;
    }
    const REMOVE_BACKREF_RE = /<a class=["&quot;]+?footnote-backref[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/g;

    jQBase.find(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        const nodeFootnote = document.getElementById($(this).attr("href").replace("#", ""));
        let tooltipContents = $(nodeFootnote).find("p").first().html().replace(REMOVE_BACKREF_RE, "");

        // replace serialized MathML HTML with its corresponding original LaTeX
        // to render with MathJax.typeset() on mouseover
        const mathItems = MathJax.startup.document.getMathItemsWithin(nodeFootnote);
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

$(document).ready(function() {
    // must wait until `$(document).ready()` to make sure MathJax has been loaded
    genFootnoteTooltips("body");
});

/**
 * Rerenders LaTeX in tooltips on show.
 */
$(document).on("inserted.bs.tooltip", function(e) {
    MathJax.typesetPromise([".tooltip"]).then(function() {
        onMathJaxTypeset(".tooltip");
    });
});
