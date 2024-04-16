const flashBackgroundColors = ["--customgreenxlight", "--custompinkxlight"];
const flashBorderColors = ["--customgreenlight", "--custompinklight"];
var flashColor_i = Math.floor(Math.random() * 2);

function customFlash(message) {
    $("#flash-text").text(message);
    $("#flash").css("background-color", `var(${flashBackgroundColors[flashColor_i]})`);
    $("#flash").css("border-color", `var(${flashBorderColors[flashColor_i]})`);
    flashColor_i = (flashColor_i + 1) % 2;
    $("#flash").removeAttr("hidden");
}

function renderQueryStringFlash() {
    var urlParams = new URLSearchParams(window.location.search);
    var flash_param = urlParams.get("flash");
    if (flash_param) {
        customFlash(decodeURIComponent(flash_param));
    }
}

$(document).ready(renderQueryStringFlash);
