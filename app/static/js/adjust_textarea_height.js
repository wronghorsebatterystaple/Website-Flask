const TEXTAREA_HEIGHT_MAX = $(window).height() * 0.6;
function adjustTextareaHeight(textarea_dom, initial) {
    // `scrollHeight` is real-time content height, `offsetHeight` is visual height that must be adjusted to `scrollheight`
    // don't change if increasing from above TEXTAREA_HEIGHT_MAX
    // hard to catch decreasing to above TEXTAREA_HEIGHT_MAX because scrollHeight is not updated until `height` is 0
    // but scroll snap on deleting text is minimal since TEXTAREA_HEIGHT_MAX makes textarea be mostly on screen
    if ((textarea_dom.offsetHeight === textarea_dom.scrollHeight
            || (textarea_dom.scrollHeight > textarea_dom.offsetHeight
                && textarea_dom.offsetHeight >= TEXTAREA_HEIGHT_MAX))
            && !initial) {
        return;
    }

    textarea_dom.style.height = "0";
    // clamp size between 7rem (roughly 4 rows) and 60vh
    var height_px = Math.max(
            7 * parseFloat(getComputedStyle(document.documentElement).fontSize),
            Math.min(TEXTAREA_HEIGHT_MAX, textarea_dom.scrollHeight));
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
