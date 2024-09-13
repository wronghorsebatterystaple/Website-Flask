let onModalLogin = function() {
    isUserAuthenticated = true;
    showAuthElems();
    $("#login-modal").modal("hide");
};

let onModalLogout = function() {
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
    const jQueryLoginModal = $("#login-modal");
    // security - wipe contents and toggle password visibility off on hide
    jQueryLoginModal.on("hidden.bs.modal", function(e) {
        const jQueryPasswordInput = $(e.target).find("#password-input");
        jQueryPasswordInput.val("");
        if (jQueryPasswordInput.attr("type") !== "password") {
            togglePasswordVisibility(jQueryPasswordInput.attr("id"), "password-show");
        }
    });

    jQueryLoginModal.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });

    // differentiate modal vs. non-modal logins for redirect
    jQueryLoginModal.find("#is_modal").val("yes");

    $("#login-form-modal").on("submit", async function(e) {
        e.preventDefault();

        let formData = new FormData(e.target, e.originalEvent.submitter);
        const respJson = await fetchWrapper(URL_LOGIN, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);

        if (respJson.success) {
            onModalLogin();
        }
    });

    $("#link--logout").on("click", async function(e) {
        e.preventDefault();

        const respJson = await fetchWrapper(URL_LOGOUT, {method: "POST"}, {previous: getCurrUrlNoParams(false)});
        doAjaxResponseForm(respJson, e);

        if (!respJson.redir_url) {
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
