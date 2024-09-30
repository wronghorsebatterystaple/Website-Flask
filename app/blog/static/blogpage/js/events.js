$(document).ready(function() {
    $("#copy-permanent-link-btn").on("click", function() {
        navigator.clipboard.writeText(PERMANENT_LINK_URL);
        customFlash(`Link copied: ${PERMANENT_LINK_URL}`);
    });
});
