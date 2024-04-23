function reloadCSRF(newToken) {
  csrf_token = newToken;
  $("input[name='csrf_token']").val(csrf_token); // reload hidden fields
}

function relogin() {
    hideAuthElems();
    $("#login-modal").load(window.location.href + " #login-modal > *");
    $("#login-modal").modal("show");
}

function showAuthElems() {
    $(".auth-false").attr("hidden", "");
    $(".auth-true").removeAttr("hidden");
}

function hideAuthElems() {
    $(".auth-true").attr("hidden", "");
    $(".auth-false").removeAttr("hidden");
}

$(document).ready(function() {
    // Security - wipe contents on hide
    $("#login-modal").on("hidden.bs.modal", function(e) {
        $(e.target).find("#password-input").val("");
    });

    $("#login-modal").on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });
});

function onLoginAjaxDone(response, e) {
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

        if (response.success) {
            showAuthElems();
            $("#login-modal").modal("hide");
        }
    }
}

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
        onLoginAjaxDone(response, e);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        var self = this;
        handleCustomErrors(jqXHR, formData, e, self, onLoginAjaxDone);
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
        data: {
            from_url: window.location.hostname + window.location.pathname
        },
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

            hideAuthElems();
        }
    });
});
