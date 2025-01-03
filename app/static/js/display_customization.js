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

const colorChoices = {
    blue: {
        form: {
            accent: "--custom-blue",
            border: "--custom-blue",
            boxShadow: "color-mix(in srgb, var(--custom-blue) 22.5%, transparent)"
        },
        flash: {
            border: "--custom-blue-light",
            background: "--custom-blue-xxxlight"
        },
        selection: "--custom-blue-xxlight"
    },
    green: {
        form: {
            accent: "--custom-green",
            border: "--custom-green",
            boxShadow: "color-mix(in srgb, var(--custom-green) 40%, transparent)"
        },
        flash: {
            border: "--custom-green",
            background: "--custom-green-xxxlight"
        },
        selection: "--custom-green-deep-xlight"
    },
    orange: {
        form: {
            accent: "--custom-orange",
            border: "--custom-orange",
            boxShadow: "color-mix(in srgb, var(--custom-orange) 30%, transparent)"
        },
        flash: {
            border: "--custom-orange-light",
            background: "--custom-orange-xxxlight"
        },
        selection: "--custom-orange-shallow-light"
    },
    pink: {
        form: {
            accent: "--custom-pink-xlight",
            border: "--custom-pink-xlight",
            boxShadow: "color-mix(in srgb, var(--custom-pink-xlight) 50%, transparent)"
        },
        flash: {
            border: "--custom-pink-xlight",
            background: "--custom-pink-deep-xxxxlight"
        },
        selection: "--custom-pink-xxlight"
    }
};
function randomizeColors() {
    const color = Object.keys(colorChoices)[Math.floor(Math.random() * Object.keys(colorChoices).length)];
    const colorChoice = colorChoices[color];
    // can't use `css()` here since it doesn't support `!important`, which is needed sometimes
    $("body").append(`
        <style>
            #flash {
                border-color: var(${colorChoice.flash.border});
                background-color: var(${colorChoice.flash.background});
            }

            ::selection {
                background-color: var(${colorChoice.selection});
            }

            :is(select, input:not([type="button"], [type="submit"]), textarea):focus {
                box-shadow: 0 0 0 0.25rem ${colorChoice.form.boxShadow} !important;
                border-color: var(${colorChoice.form.border}) !important;
            }
            
            /* probably won't work yet, maybe in the future though :( */
            input.is([type="checkbox"], [type="radio"]) {
                accent-color: var(${colorChoice.form.accent}) !important;
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
