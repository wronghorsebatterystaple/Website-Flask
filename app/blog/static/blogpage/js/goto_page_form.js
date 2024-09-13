$(document).ready(function() {
    $("#goto-page-form").on("submit", function(e) {
        e.preventDefault();

        // non-state-changing GET shouldn't need CSRF protection
        let page = parseInt($("#input--page").val(), 10);
        if (!isNaN(page) && page <= totalPages && page > 0) {
            window.location.href = window.location.pathname + `?page=${page}`;
        } 
    });
});
