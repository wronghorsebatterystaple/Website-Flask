/* Wait for `$(document).ready` to give time for changing `backgroundImgOverrideName` on JS load.
 * Must use `insertRule()` instead of CSS variable, otherwise DarkReader fails to display the image in dark mode. */
$(document).ready(function() {
    if (URL_backgroundImgOverride !== "") {
        document.styleSheets[0].insertRule(`#background-img { background-image: url(${URL_backgroundImgOverride}) }`);
    } else {
        document.styleSheets[0].insertRule(`#background-img { background-image: url(${URL_BACKGROUND_IMG_DEFAULT}) }`);
    }
});
