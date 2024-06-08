$(document).ready(function() {
    $("#copy-permanent-link").on("click", function() {
        navigator.clipboard.writeText(URL_ABS_BLOGS_BASE + POST_ID);
        customFlash("Link copied! Installing malware…");
    });
});
