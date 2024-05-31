function refreshTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Rerender LaTeX in tooltips on show
$(document).on("inserted.bs.tooltip",  function(e) {
    MathJax.typesetPromise([".tooltip"]).then(function() {
        onMathJaxTypeset(".tooltip");
    });
});
