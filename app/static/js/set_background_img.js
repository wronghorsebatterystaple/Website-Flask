/* CSSStyleSheet used since URLs within CSS `var()` are not detected by DarkReader, and JQuery `css()` is inline
 * which we want to try and avoid */
const styleSheetBackgroundImg = new CSSStyleSheet();
document.adoptedStyleSheets.push(styleSheetBackgroundImg);

function reloadBackgroundImg() {
    if (urlBackgroundImageOverride !== "") {
        styleSheetBackgroundImg.replaceSync(
                `#background-img { background-image: url(${urlBackgroundImageOverride}) }`);
    } else {
        styleSheetBackgroundImg.replaceSync(
                `#background-img { background-image: url(${URL_BACKGROUND_IMG_DEFAULT}) }`);
    }
}

/* Wait for `$(document).ready` to give time for changing `backgroundImgOverrideName` on JS load */
$(document).ready(function() {
    reloadBackgroundImg();
});
