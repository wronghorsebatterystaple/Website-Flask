const MAX_TEXTBOX_HEIGHT = $(window).height() * 0.6;
function adjustTextareaHeight(textarea_dom, initial) {
    // don't change if increasing from above MAX_TEXTBOX_HEIGHT
    // hard to catch decreasing to above MAX_TEXTBOX_HEIGHT because scrollHeight is not updated until `height = "0"`
    // but scroll snap on deleting text should be minimal since MAX_TEXTBOX_HEIGHT forces whole textarea to be on screen
    if ((textarea_dom.offsetHeight === textarea_dom.scrollHeight
            || (textarea_dom.scrollHeight > textarea_dom.offsetHeight
                    && textarea_dom.offsetHeight >= MAX_TEXTBOX_HEIGHT))
            && !initial) {
        return;
    }

    textarea_dom.style.height = "0";
    // clamp size between 7rem (roughly 4 rows) and 60vh
    var height_px = Math.max(7 * parseFloat(getComputedStyle(document.documentElement).fontSize),
            Math.min(MAX_TEXTBOX_HEIGHT, textarea_dom.scrollHeight));
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
