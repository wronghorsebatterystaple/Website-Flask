const IS_FIREFOX = navigator.userAgent.toLowerCase().includes("firefox");
let styleSheetColors = null;
// with Firefox, DarkReader doesn't affect `adoptedStyleSheets` properly and uses some weird fallback thing
if (IS_FIREFOX) {
    styleSheetColors = document.styleSheets[0];
} else {
    styleSheetColors = new CSSStyleSheet();
    document.adoptedStyleSheets.push(styleSheetColors);
}
randomizeColors();

// it seems like this doesn't *have* to be before dark mode, but putting it before just because it makes sense
function randomizeColors() {
    const colorChoicesSelection = ["--custom-blue-xxlight", "--custom-green-deep-xlight", "--custom-pink-xxlight"];
    let rand = Math.floor(Math.random() * colorChoicesSelection.length);
    styleSheetColors.insertRule(`
        ::selection {
            background-color: var(${colorChoicesSelection[rand]}) !important;
        }
    `);

    const colorChoicesFlash = [
        ["--custom-blue", "--custom-blue-xxxlight"],
        ["--custom-green", "--custom-green-xxxlight"],
        ["--custom-orange-light", "--custom-orange-xxxlight"],
        ["--custom-pink-xlight", "--custom-pink-xxxlight"]
    ];
    rand = Math.floor(Math.random() * colorChoicesFlash.length);
    styleSheetColors.insertRule(`
        .flash {
            border-color: var(${colorChoicesFlash[rand][0]}) !important;
            background-color: var(${colorChoicesFlash[rand][1]}) !important;
        }
    `);
}
