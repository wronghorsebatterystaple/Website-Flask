$(document).ready(function() {
    // Markdown tweaks more appropriate for JQuery than Markdown custom syntax extensions or Flask
    var postContent_elem = $("#post-content");
    postContent_elem.children("h1").addClass("post-h1");
    postContent_elem.children("h2").addClass("post-h2");
});
