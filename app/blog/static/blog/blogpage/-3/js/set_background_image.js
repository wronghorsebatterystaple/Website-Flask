function setBackgroundImage() {
    var i = Math.floor(Math.random() * 3);
    var imgContainer_elem = $("#background-img");
    imgContainer_elem.css("background-image", `url(${path_backgroundImg}/background_${i}.svg`);
    imgContainer_elem.css("background-repeat", "no-repeat");
    imgContainer_elem.css("background-position", "center center");
    imgContainer_elem.css("background-size", "clamp(42.5vw, 816px, 100vw) auto");
    imgContainer_elem.css("background-attachment", "fixed"); // not supported on iOS
}
