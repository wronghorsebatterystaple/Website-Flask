function adjustTextareaHeight(textarea_dom, initial) {
    var maxHeight = $(window).height() * 0.5;
    // don't change if increasing from above maxHeight
    // can't seem to catch decreasing to above maxHeight because scrollHeight is not updated until `height = "0"`
    // but scroll snap on deleting text should be minimal since maxHeight forces the whole textarea to be on screen
    if ((textarea_dom.offsetHeight === textarea_dom.scrollHeight
            || (textarea_dom.scrollHeight > textarea_dom.offsetHeight && textarea_dom.offsetHeight >= maxHeight))
            && !initial) {
        return;
    }

    textarea_dom.style.height = "0";
    // clamp size between 7rem (roughly 4 rows) and 50vh
    var height_px = Math.max(7 * parseFloat(getComputedStyle(document.documentElement).fontSize),
            Math.min(maxHeight, textarea_dom.scrollHeight));
    textarea_dom.style.height = `${height_px + 1.5}px`; // + 1.5 to hide scrollbar
}

$(document).ready(function() {
    $("textarea").each(function() {
        adjustTextareaHeight($(this).get(0), true);
    });

    $("textarea").on("input", function(e) {
        adjustTextareaHeight(e.target, false);
    });
});
