function relogin() {
    customFlash("Your session has expired (or you were being sneaky...). Please log in again.");
    hideAuthElems();
    var loginModal_elem = $("#login-modal");
    loginModal_elem.load(window.location.href + " #login-modal > *");
    loginModal_elem.modal("show");
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
    var loginModal_elem = $("#login-modal");
    // security - wipe contents on hide
    loginModal_elem.on("hidden.bs.modal", function(e) {
        $(e.target).find("#password-input").val("");
    });

    loginModal_elem.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });
});

function onLoginAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);

    if (response.success) {
        showAuthElems();
        $("#login-modal").modal("hide");
    }
}

$(document).on("submit", "#login-form-modal", function(e) {
    e.preventDefault();

    var formData = new FormData($(this).get(0), $(e.originalEvent.submitter).get(0));
    // differentiate modal vs. non-modal logins for redirect; doesn't work anywhere else
    formData.set("is_modal", "yes");
    $.ajax({
        type: "POST",
        url: $("#var-login-url").attr("data-val"),
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
        handleCustomErrors(jqXHR, formData, e, self, onLoginAjaxDone);
    });
});

$(document).on("click", "#logout-link", function(e) {
    e.preventDefault();

    $.ajax({
        type: "GET",
        url: $("#var-logout-url").attr("data-val"),
        crossDomain: true,
        data: {
            from_url: window.location.hostname + window.location.pathname // to determine if we need to redirect away
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
