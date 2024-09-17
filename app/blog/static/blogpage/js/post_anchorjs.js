const ANCHORJS_OPTIONS = {
    class: "anchorjs-anchor",
    icon: "\uF470",
    placement: "right"
};

function addPostAnchors() {
    $().addClass("anchorjs-anchor");
    anchors.options = ANCHORJS_OPTIONS;
    anchors.add(".post__h1, .post__h2");

    $(".anchorjs-anchor").on("click", function(e) {
        const jQueryHeading = $(e.target).parent();
        if (jQueryHeading.length <= 0) {
            return;
        }

        let link = `${URL_PERMANENT_LINK}#${jQueryHeading.attr("id")}`;
        navigator.clipboard.writeText(link);
        customFlash(`Link copied: ${link}`);
    });
}

addPostAnchors();
