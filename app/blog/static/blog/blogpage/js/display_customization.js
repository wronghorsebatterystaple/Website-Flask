$(document).ready(function() {
    // Markdown tweaks more appropriate for JQuery than Markdown custom syntax extensions or Flask
    $("#post-content").find("a").addClass("link-customblue");
    $("#post-content").children("h1").addClass("post-h1");
    $("#post-content").children("h2").addClass("post-h2");
});
