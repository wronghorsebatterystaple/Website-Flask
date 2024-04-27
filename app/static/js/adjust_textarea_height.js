function adjustTextareaHeight(textarea_dom, initial) {
    var maxHeight = $(window).height() * 0.6;
    if ((textarea_dom.offsetHeight === textarea_dom.scrollHeight || textarea_dom.scrollHeight >= maxHeight) && !initial) {
        return;
    }

    textarea_dom.style.height = "0";
    // clamp size between 7rem (roughly 4 rows) and 50vh
    var height_px = Math.max(7 * parseFloat(getComputedStyle(document.documentElement).fontSize),
            Math.min(maxHeight, textarea_dom.scrollHeight));
    console.log(`${textarea_dom.scrollHeight}, ${height_px}`);
    textarea_dom.style.height = `${height_px + 1.5}px`; // + 1.5 to hide scrollbar
}

$(document).ready(function() {
    $("textarea").each(function() {
        adjustTextareaHeight($(this).get(0), true);
    });
});

$(document).on("input", "textarea", function(e) {
    adjustTextareaHeight(e.target, false);
});
