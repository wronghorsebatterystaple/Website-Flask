$(document).ready(function() {
    $("#btn--copy-permanent-link").on("click", function() {
        navigator.clipboard.writeText(URL_PERMANENT_LINK);
        customFlash(`Link copied: ${URL_PERMANENT_LINK}`);
    });
});
