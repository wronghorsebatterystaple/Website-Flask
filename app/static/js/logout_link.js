$(document).on("click", "#logout-link", function(e) {
    e.preventDefault();

    $.ajax({
        type: "GET",
        url: $("#var-url-for-logout").attr("data-val"),
        crossDomain: true,
        xhrFields: {
            withCredentials: true
        },
        dataType: "json"
    })
    .done(function(response) {
        if (response.flash_message) {
            customFlash(response.flash_message);
        }

        $("#login-or-logout").load(window.location.href + " #login-or-logout > *");
    });
});
