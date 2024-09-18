$(document).ready(function() {
    $("#goto-page-form").on("submit", function(e) {
        e.preventDefault();

        // non-state-changing GET shouldn't need CSRF protection
        let pageNum = parseInt($("#input--page").val(), 10);
        if (isNaN(pageNum) || pageNum <= 0 || pageNum > TOTAL_PAGES) {
            customFlash("haker :3");
            return;
        }

        window.location.href = window.location.pathname + `?page=${pageNum}`;
    });
});
