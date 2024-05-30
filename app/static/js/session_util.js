function showAuthElems() {
    $(".auth-false").attr("hidden", "");
    $(".auth-true").removeAttr("hidden");
}

function hideAuthElems() {
    $(".auth-true").attr("hidden", "");
    $(".auth-false").removeAttr("hidden");
}

function onLoginAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);

    if (response.success) {
        showAuthElems();
        $("#login-modal").modal("hide");
    }
}

$(document).ready(function() {
    var loginModal_elem = $("#login-modal");
    // Security - wipe contents on hide
    loginModal_elem.on("hidden.bs.modal", function(e) {
        $(e.target).find("#password-input").val("");
    });

    loginModal_elem.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });

    // Differentiate modal vs. non-modal logins for redirect
    loginModal_elem.find("#is_modal").val("yes");

    $("#login-form-modal").on("submit", function(e) {
        e.preventDefault();

        var formData = new FormData(e.target, e.originalEvent.submitter);
        $.ajax({
            type: "POST",
            url: URL_login,
            crossDomain: true,
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
            handleAjaxErrors(jqXHR, formData, e, self, onLoginAjaxDone);
        });
    });

    $("#logout-link").on("click", function(e) {
        e.preventDefault();

        $.ajax({
            type: "GET",
            url: URL_logout,
            crossDomain: true,
            data: {
                previous: window.location.hostname + window.location.pathname // to determine if we need to redirect away
            },
            dataType: "json"
        })
        .done(function(response) {
            if (response.redirect_abs_url) {
                var newURL = new URL(decodeURIComponent(response.redirect_abs_url));
                if (response.flash_message) {
                    newURL.searchParams.append("flash", encodeURIComponent(response.flash_message));
                }
            window.location.href = newURL;
            } else {
                if (response.flash_message) {
                    customFlash(response.flash_message);
                }

                hideAuthElems();
            }
        });
    });
});
