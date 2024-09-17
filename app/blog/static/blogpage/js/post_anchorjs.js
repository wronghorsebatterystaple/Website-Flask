const ANCHORJS_OPTIONS = {
    icon: "\uF470",
    placement: "right"
};

function addPostAnchors() {
    $(".post__h1, .post__h2").addClass("anchorjs-anchor");
    anchors.options = ANCHORJS_OPTIONS;
    anchors.add(".anchorjs-anchor");
}
