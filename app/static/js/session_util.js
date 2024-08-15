var onModalLogin = function() {
    isUserAuthenticated = true;
    showAuthElems();
    $("#login-modal").modal("hide");
};

var onModalLogout = function() {
    isUserAuthenticated = false;
    hideAuthElems();
};

function relogin() {
    customFlash("Your session has expired (or you were being sneaky). Please log in.");
    hideAuthElems();
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
    const elemLoginModal = $("#login-modal");
    // security - wipe contents and toggle password visibility off on hide
    elemLoginModal.on("hidden.bs.modal", function(e) {
        const elemPasswordInput = $(e.target).find("#password-input");
        elemPasswordInput.val("");
        if (elemPasswordInput.attr("type") !== "password") {
            togglePasswordVisibility(elemPasswordInput.attr("id"), "password-show");
        }
    });

    elemLoginModal.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });

    // differentiate modal vs. non-modal logins for redirect
    elemLoginModal.find("#is_modal").val("yes");

    $("#login-form-modal").on("submit", async function(e) {
        e.preventDefault();

        let formData = new FormData(e.target, e.originalEvent.submitter);
        const responseJSON = await fetchWrapper(URL_LOGIN, { method: "POST", body: formData });
        doAjaxResponseForm(responseJSON, e);

        if (responseJSON.success) {
            onModalLogin();
        }
    });

    $("#logout-link").on("click", async function(e) {
        e.preventDefault();

        const responseJSON = await fetchWrapper(
                URL_LOGOUT,
                { method: "POST" },
                { previous: getCurrentUrlNoParams(false) });
        doAjaxResponseForm(responseJSON, e);

        if (!responseJSON.redirect_url) {
            onModalLogout();
        }
    });

    $("#login-modal").on("show.bs.modal", function(e) {
        if (window.location.href.startsWith(URL_LOGIN)) {
            e.preventDefault();
            customFlash("You're already on the login page, you doofus.");
        }
    });
});
