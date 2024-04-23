function relogin() {
    $("#login-modal").load(window.location.href + " #login-modal > *");
    $("form").each(function() { // make sure all have id to reload CSRF token
        $(this).load(window.location.href + ` #${$(this).attr("id")} > *`);
    });
    $("#login-modal").modal("show");
}
