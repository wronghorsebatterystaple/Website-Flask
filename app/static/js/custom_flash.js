function customFlash(message) {
    $("#flash-text").text(message);
    $("#flash").removeAttr("hidden");
}

function renderQueryStringFlash() {
    var urlParams = new URLSearchParams(window.location.search);
    var flash_param = urlParams.get("flash");
    if (flash_param) {
        customFlash(decodeURIComponent(flash_param));
    }
}

window.addEventListener("pageshow", renderQueryStringFlash, false); // this fires even if page is cached
