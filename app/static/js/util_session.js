let onModalLogin = function() {
    isUserAuthenticated = true;
    showAuthElems();
    $("#modal-login").modal("hide");
};

let onModalLogout = function() {
    isUserAuthenticated = false;
    hideAuthElems();
};

function relogin() {
    customFlash("Your session has expired (or you were being sneaky). Please log in.");
    hideAuthElems();
    $("#modal-login").modal("show");
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
    const jQModalLogin = $("#modal-login");
    // security - wipe contents and toggle password visibility off on hide
    jQModalLogin.on("hidden.bs.modal", function(e) {
        const jQInputPassword = $(e.target).find("#password-input");
        jQInputPassword.val("");
        if (jQInputPassword.attr("type") !== "password") {
            togglePasswordVisibility(jQInputPassword.attr("id"), "password-show");
        }
    });

    jQModalLogin.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });

    // differentiate modal vs. non-modal logins for redirect
    jQModalLogin.find("#is_modal").val("true");

    $("#modal-login__form").on("submit", async function(e) {
        e.preventDefault();

        let formData = new FormData(e.target, e.originalEvent.submitter);
        const respJson = await fetchWrapper(URL_LOGIN, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);

        if (respJson.success) {
            onModalLogin();
        }
    });

    $("#logout-link").on("click", async function(e) {
        e.preventDefault();

        const respJson = await fetchWrapper(URL_LOGOUT, {method: "POST"}, {previous: URL_CURRENT_NO_QS});
        doAjaxResponseForm(respJson, e);

        if (!respJson.redir_url) {
            onModalLogout();
        }
    });

    $("#modal-login").on("show.bs.modal", function(e) {
        if (window.location.href.startsWith(URL_LOGIN)) {
            e.preventDefault();
            customFlash("You're already on the login page, you doofus.");
        }
    });
});
