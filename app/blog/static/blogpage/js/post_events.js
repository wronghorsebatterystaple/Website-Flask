$(document).ready(function() {
    $("#copy-permanent-link-btn").on("click", function() {
        navigator.clipboard.writeText(PERMANENT_LINK_URL);
        customFlash(`Link copied: ${PERMANENT_LINK_URL}`);
    });

    $(".heading-link").on("click", function(e) {
        let url = PERMANENT_LINK_URL + e.target.getAttribute("href");
        navigator.clipboard.writeText(url);
        customFlash(`Link copied: ${url}`);
    });
});
