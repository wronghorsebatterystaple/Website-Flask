const ANCHORJS_OPTIONS = {
    icon: "\uF470",
    placement: "right",
    truncate: 1000
};

function addPostAnchors() {
    anchors.options = ANCHORJS_OPTIONS;
    anchors.add(".post__h1, .post__h2");

    $(".anchorjs-link").on("click", function(e) {
        const jQHeading = $(e.target).parent();
        if (jQHeading.length <= 0) {
            return;
        }

        let link = `${PERMANENT_LINK_URL}#${jQHeading.attr("id")}`;
        navigator.clipboard.writeText(link);
        customFlash(`Link copied: ${link}`);
    });
}

addPostAnchors();
