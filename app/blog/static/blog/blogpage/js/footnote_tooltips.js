window.addEventListener("load", function() {
    const REMOVE_BACKREF_RE = /<a class="footnote-backref"[\S\s]*?<\/a>/;
    const MATCH_MATHJAX_RE = /<mjx-container[\S\s]*?<\/mjx-container>/;

    $(".footnote-ref").each(function() {
        $(this).attr("data-bs-toggle", "tooltip").attr("data-bs-html", "true");
        var footnote_dom = document.getElementById($(this).attr("href").replace("#", ""));
        var footnote_html = $(footnote_dom).find("p").html().replace(REMOVE_BACKREF_RE, "");
        
        const mathItems = MathJax.startup.document.getMathItemsWithin(footnote_dom);
        const matches = footnote_html.match(MATCH_MATHJAX_RE);
        if (matches != null) {
            for (var i = 0; i < matches.length; i++) {
                var match = matches[i];
                footnote_html.replace(match, mathItems[i].math);
            }
        }

        $(this).attr("data-bs-title", footnote_html);
    });

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

$(document).on("mouseover", ".footnote-ref", function(e) {
    MathJax.typeset();
});
