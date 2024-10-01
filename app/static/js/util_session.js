let onModalLogin = function() {
    isUserAuthenticated = true;
    showLoggedInElems();
    $("#modal-login").modal("hide");
};

let onModalLogout = function() {
    isUserAuthenticated = false;
    showLoggedOutElems();
};

function relogin() {
    customFlash("Your session has expired (or you were being sneaky). Please log in.");
    onModalLogout();
    $("#modal-login").modal("show");
}

function showLoggedInElems() {
    $(".show-when-logged-out").attr("hidden", "");
    $(".show-when-logged-in").removeAttr("hidden");
}

function showLoggedOutElems() {
    $(".show-when-logged-in").attr("hidden", "");
    $(".show-when-logged-out").removeAttr("hidden");
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
        const respJson = await fetchWrapper(LOGIN_URL, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);

        if (respJson.success) {
            onModalLogin();
        }
    });

    $("#logout-link").on("click", async function(e) {
        e.preventDefault();

        const respJson = await fetchWrapper(LOGOUT_URL, {method: "POST"});
        doAjaxResponseForm(respJson, e);
        onModalLogout();
    });

    $("#modal-login").on("show.bs.modal", function(e) {
        if (window.location.href.startsWith(LOGIN_URL)) {
            e.preventDefault();
            customFlash("You're already on the login page, you doofus.");
        }
    });
});
