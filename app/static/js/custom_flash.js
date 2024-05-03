function customFlash(message) {
    $("#flash-text").text(message);
    $("#flash").removeAttr("hidden");
}

function renderQueryStringFlash() {
    var urlParams = new URLSearchParams(window.location.search);
    var flash = urlParams.get("flash");
    if (flash) {
        customFlash(decodeURIComponent(flash));
    }
}

$(document).ready(renderQueryStringFlash);
