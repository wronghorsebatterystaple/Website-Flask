function applyGlobalStyles(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length <= 0) {
        return;
    }

    // tables and non-table code blocks scroll horizontally on overflow
    jQBase.find("table").wrap(HORIZ_SCOLL_DIV_HTML);
    jQBase.find("pre").each(function() {
        if ($(this).parents("table").length === 0) {
            $(this).wrap(HORIZ_SCOLL_DIV_HTML);
        }
    });

    // inline CSS used by Markdown tables converted to class for CSP
    jQBase.find("[style='text-align: center;']").removeAttr("style").addClass("text-center");
    jQBase.find("[style='text-align: right;']").removeAttr("style").addClass("text-end");

    // no extra space between lists and their "heading" text
    jQBase.find("ol, ul").prev("p").addClass("mb-0");

    // footnote tweaks
    const jQFootnotes = jQBase.find(".footnote").first();
    if (jQFootnotes.length > 0) {
        jQFootnotes.attr("id", "footnotes");
        jQFootnotes.wrap("<details id=\"footnotes__details\" class=\"footnotes__details\"></details>")
        jQFootnotes.before("<summary class=\"footnotes__details-summary\">Footnotes</summary>");

        jQFootnotes.find("p").addClass("mb-0");
        const jQFootnotesList = jQFootnotes.children("ol").first();
        jQFootnotesList.addClass("mb-0");
        jQFootnotesList.children("li").addClass("mb-1");
    }

    // footnotes collapsible opens if footnote link clicked on and the collapsible is closed
    jQBase.find(".footnote-ref").on("click", function(e) {
        const jQFootnotesDetails = jQBase.find("#footnotes__details");
        if (!jQFootnotesDetails.is("[open]")) {
            jQFootnotesDetails.attr("open", "");
        }
    });
    
    applyCustomMarkdown(baseSelector); // Markdown tweaks round 3
    applySyntaxHighlighting(baseSelector);
}

function applyCustomMarkdown(baseSelector) {
    const jQBase = $(baseSelector);
    if (jQBase.length <= 0) {
        return;
    }

    // custom table horizontal and vertical align syntax
    jQBase.find("[data-align-center]").parents("th, td").addClass("text-center");
    jQBase.find("[data-align-right]").parents("th, td").addClass("text-end");
    jQBase.find("[data-align-top]").parents("th, td").addClass("align-top");
    jQBase.find("[data-align-bottom]").parents("th, td").addClass("align-bottom");

    // custom table column width syntax
    jQBase.find("[data-col-width]").parents("th, td").attr("width", $(this).attr("data-col-width"));

    // no extra `<p>` tags in custom figures/captions
    jQBase.find(".md-captioned-figure").find("p").children("img").unwrap();
}

function applySyntaxHighlighting(baseSelector) {
    $(baseSelector).find("pre code").each(function() {
        if ($(this).parents("table").length === 0) {
            hljs.highlightElement($(this).get(0));
            $(this).addClass("code-block--outside");
        }
    });
}

function randomizeFlashColor() {
    const colorChoices = [
        ["--custom-blue-light", "--custom-blue-xxxlight"],
        ["--custom-green", "--custom-green-xxxlight"],
        ["--custom-orange-light", "--custom-orange-xxxlight"],
        ["--custom-pink-xlight", "--custom-pink-xxxlight"]
    ];
    rand = Math.floor(Math.random() * colorChoices.length);
    // can't use `css()` here since it doesn't support `!important`, which is needed
    $("body").append(`
        <style>
            #flash {
                border-color: var(${colorChoices[rand][0]}) !important;
                background-color: var(${colorChoices[rand][1]}) !important
            }
        </style>
    `);
}

function randomizeSelectionColor() {
    const colorChoices = ["--custom-blue-xxlight", "--custom-green-deep-xlight", "--custom-pink-xxlight"];
    let rand = Math.floor(Math.random() * colorChoices.length);
    $("body").append(`
        <style>
            ::selection {
                background-color: var(${colorChoices[rand]}) !important;
            }
        </style>
    `);
}

function reloadBackgroundImg() {
    if (urlBackgroundImgOverride !== "") {
        $("#background-img").css("background-image", `url(${urlBackgroundImgOverride})`);
    } else {
        $("#background-img").css("background-image", `url(${URL_BACKGROUND_IMG_DEFAULT})`);
    }
}

applyGlobalStyles("body");
randomizeFlashColor();
randomizeSelectionColor();
reloadBackgroundImg();
