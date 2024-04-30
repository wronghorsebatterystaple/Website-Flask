$(document).on("submit", "#goto-page-form", function(e) {
    e.preventDefault();

    // non-state-changing GET shouldn't need CSRF protection
    var page = parseInt($("#page-input").val(), 10);
    if (!isNaN(page) && page > 0) {
        window.location.href = window.location.pathname + `?page=${page}`;
    } 
});
