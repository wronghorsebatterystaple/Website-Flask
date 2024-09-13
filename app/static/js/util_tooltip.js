function refreshTooltips(baseSelector) {
    const nodeBase = document.querySelector(baseSelector);
    if (!nodeBase) {
        return;
    }

    const tooltipTriggerList = nodeBase.querySelectorAll('[data-bs-toggle="tooltip"]');
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
