function customFlash(message) {
    $("#flash__text").text(message); // `text()` by itself is XSS-safe
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
$(document).on("close.bs.alert", "#flash", function(e) {
    const nodeDuplicate = e.target.cloneNode(true);
    nodeDuplicate.setAttribute("hidden", "");
    document.getElementById("flash__wrapper").append(nodeDuplicate);
});
