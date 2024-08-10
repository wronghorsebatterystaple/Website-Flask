/* CSSStyleSheet used since URLs within CSS `var()` are not detected by DarkReader, and JQuery `css()` is inline
 * which we want to try and avoid */
const backgroundImgStyleSheet = new CSSStyleSheet();
document.adoptedStyleSheets.push(backgroundImgStyleSheet);

function reloadBackgroundImg() {
    if (URLBackgroundImageOverride !== "") {
        backgroundImgStyleSheet.replaceSync(
                `#background-img { background-image: url(${URLBackgroundImageOverride}) }`);
    } else {
        backgroundImgStyleSheet.replaceSync(
                `#background-img { background-image: url(${URL_BACKGROUND_IMG_DEFAULT}) }`);
    }
}

/* Wait for `$(document).ready` to give time for changing `backgroundImgOverrideName` on JS load */
$(document).ready(function() {
    reloadBackgroundImg();
});
