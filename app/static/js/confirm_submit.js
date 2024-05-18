$(document).ready(function() {
    $("input[data-confirm-submit][type='submit']").on("click", function() {
        return confirm("Sanity check");
    });
});
