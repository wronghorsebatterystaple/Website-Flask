function setBackgroundImage() {
    var imgContainer_elem = $("#background-img");
    imgContainer_elem.css("background-image", `url(${$("#var-path-to-background-image").attr("data-val")}background_0.svg`);
    imgContainer_elem.css("background-repeat", "no-repeat");
    imgContainer_elem.css("background-repeat", "no-repeat");
    imgContainer_elem.css("background-position", "center center");
    imgContainer_elem.css("background-size", "cover");
    imgContainer_elem.css("background-attachment", "fixed");
}
