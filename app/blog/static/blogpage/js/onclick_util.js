$(document).ready(function() {
    $("#copy-permanent-link-btn").on("click", function() {
        navigator.clipboard.writeText(URL_PERMANENT_LINK);
        customFlash(`Link copied: ${URL_PERMANENT_LINK}`);
    });
});
