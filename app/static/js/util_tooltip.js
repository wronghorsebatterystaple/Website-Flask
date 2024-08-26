function refreshTooltips(baseSelector) {
    const domBase = document.querySelector(baseSelector);
    if (!domBase) {
        return;
    }

    const tooltipTriggerList = domBase.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Rerenders LaTeX in tooltips on show.
 */
$(document).on("inserted.bs.tooltip", function(e) {
    MathJax.typesetPromise([".tooltip"]).then(function() {
        onMathJaxTypeset(".tooltip");
    });
});
