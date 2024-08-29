function customFlash(message) {
    $("#flash-text").text(message); // text() by itself is XSS-safe
    $("#flash").removeAttr("hidden");
}

function renderQueryStringFlash() {
    let urlParams = new URLSearchParams(window.location.search);
    let flash = urlParams.get("flash_msg");
    if (flash) {
        customFlash(decodeURIComponent(flash));
    }
}

$(document).ready(renderQueryStringFlash);

/**
 * Regenerates flash element on dismiss so we can flash again.
 * We do this instead of changing close button behavior to preserve the fade animation.
 */
$(document).on("close.bs.alert", "#flash", function() {
    $("#non-navbar").prepend("<div id=\"flash\" class=\"flash alert alert-info alert-dismissible fade show\" role=\"alert\" hidden=\"\"><span id=\"flash-text\"></span><button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\" aria-label=\"Dismiss\"></button></div>");
});
