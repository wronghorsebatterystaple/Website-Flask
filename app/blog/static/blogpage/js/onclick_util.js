$(document).ready(function() {
    $("#copy-permanent-link-btn").on("click", function() {
        navigator.clipboard.writeText(URL__PERMANENT_LINK);
        customFlash("Link copied!");
    });
});
