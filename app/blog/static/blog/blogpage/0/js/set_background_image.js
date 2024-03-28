function setBackgroundImage() {
    var i = Math.floor(Math.random() * 4);
    var mainContainer_elem = $("#background-img");
    mainContainer_elem.css("background-image", `url(https://blog.anonymousrand.xyz/static/blog/images/background/background_${i}.svg`);
    mainContainer_elem.css("background-repeat", "no-repeat");
    mainContainer_elem.css("background-position", "center center");
    mainContainer_elem.css("background-size", "clamp(48vw, 921px, 100vw) auto");
    mainContainer_elem.css("background-attachment", "fixed");
}
