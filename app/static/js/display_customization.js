function applyGlobalStyles(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length === 0) {
        return;
    }

    // tables and non-table code blocks scroll horizontally on overflow
    jQBase.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    jQBase.find("pre").each(function() {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(HORIZ_SCOLL_DIV_HTML);
        }
    });

    applySyntaxHighlighting(baseSelector);
}

function applySyntaxHighlighting(baseSelector) {
    $(baseSelector).find("pre code").each(function() {
        if ($(this).parents("table").length === 0) {
            hljs.highlightElement($(this).get(0));
            $(this).addClass("code-block-outside-table");
        }
    });
}

function randomizeColors() {
    const colorChoices = {
        blue: {
            flash: {border: "--custom-blue-light", background: "--custom-blue-xxxlight"},
            selection: "--custom-blue-xxlight"
        },
        green: {
            flash: {border: "--custom-green", background: "--custom-green-xxxlight"},
            selection: "--custom-green-deep-xlight"
        },
        orange: {
            flash: {border: "--custom-orange-light", background: "--custom-orange-xxxlight"},
            selection: "--custom-orange-shallow-light"
        },
        pink: {
            flash: {border: "--custom-pink-xxlight", background: "--custom-pink-xxxxlight"},
            selection: "--custom-pink-xxxlight"
        }
    };
    const color = Object.keys(colorChoices)[Math.floor(Math.random() * Object.keys(colorChoices).length)];
    const colorChoice = colorChoices[color];
    // can't use `css()` here since it doesn't support `!important`, which is needed
    $("body").append(`
        <style>
            #flash {
                border-color: var(${colorChoice.flash.border}) !important;
                background-color: var(${colorChoice.flash.background}) !important
            }

            ::selection {
                background-color: var(${colorChoice.selection}) !important;
            }
        </style>
    `);
}

function reloadBackgroundImg() {
    if (backgroundImgUrl !== "") {
        $("#background-img").css("background-image", `url(${backgroundImgUrl})`);
    } else {
        $("#background-img").css("background-image", `url(${DEFAULT_BACKGROUND_IMG_URL})`);
    }
}

randomizeColors();
applyGlobalStyles("body");
reloadBackgroundImg();
// for making sure navigating to a URL fragment doesn't hide it in the sticky navbar
document.documentElement.style.setProperty("--navbar-outer-height", `${$("#navbar").outerHeight()}px`);
