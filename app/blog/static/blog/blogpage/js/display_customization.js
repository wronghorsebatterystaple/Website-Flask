$(document).ready(function() {
    // Markdown tweaks round 3
    var postContent_elem = $("#post-content");
    postContent_elem.children("h1").addClass("post-h1");
    postContent_elem.children("h2").addClass("post-h2");
    postContent_elem.find("img").addClass("post-img");
});
