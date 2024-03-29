function setBackgroundImage() {
    var i = Math.floor(Math.random() * 4);
    var imgContainer_elem = $("#background-img");
    imgContainer_elem.css("background-image", `url(https://blog.anonymousrand.xyz/static/blog/blogpage/0/images/background/background_${i}.svg`);
    imgContainer_elem.css("background-repeat", "no-repeat");
    imgContainer_elem.css("background-position", "center center");
    imgContainer_elem.css("background-size", "clamp(42.5vw, 816px, 100vw) auto");
    imgContainer_elem.css("background-attachment", "fixed"); // not supported on iOS
}
