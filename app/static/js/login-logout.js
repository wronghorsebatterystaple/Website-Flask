$(document).on("submit", "#login-form", function(e) {
    e.preventDefault();

    var formData = new FormData($(this).get(0), $(e.originalEvent.submitter).get(0));
    $.ajax({
        type: "POST",
        url: $("#var-login-url").attr("data-val"),
        crossDomain: true,
        xhrFields: {
            withCredentials: true
        },
        data: formData,
        processData: false,
        contentType: false,
        dataType: "json"
    })
    .done(function(response) {
        if (response.redirect_uri) {
            var newURI = response.redirect_uri;
            if (response.flash_message) {
                newURI += `?flash=${encodeURIComponent(response.flash_message)}`;
            }
            window.location.href = newURI;
        } else {
            if (response.flash_message) {
                customFlash(response.flash_message);
            }
            
            if (response.submission_errors) { 
                errors = response.submission_errors;
                Object.keys(errors).forEach((field_name) => {
                    var field_elem = $(e.target).find(`#${field_name}-field`)
                    field_elem.find(`#${field_name}-input`).addClass("is-invalid");
                    field_elem.find(".invalid-feedback").text(errors[field_name][0]);
                });
            }

            $("#login-or-logout").load(window.location.href + " #login-or-logout > *");
        }
    });
});

$(document).on("click", "#logout-link", function(e) {
    e.preventDefault();

    $.ajax({
        type: "GET",
        url: $("#var-logout-url").attr("data-val"),
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
