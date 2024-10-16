const IS_USER_AUTHENTICATED = async function() {
    const respJson = await fetchWrapper(SESSION_STATUS_URL, {method: "GET"});
    return respJson.logged_in;
};

let onSamePageLogin = function() {
    $("#login-modal").modal("hide");
    $(".show-when-logged-out").attr("hidden", "");
    $(".show-when-logged-in").removeAttr("hidden");
};

let onSamePageLogout = function() {
    $(".show-when-logged-in").attr("hidden", "");
    $(".show-when-logged-out").removeAttr("hidden");
};

async function checkSessionExpiry() {
    if (await IS_USER_AUTHENTICATED()) {
        return;
    }

    const resp = await fetch(window.location.href, {method: "GET", credentials: "include", mode: "cors"});
    if (resp.redirected || resp.status !== 200) { // `302` redirects give the status of the *post-redirect* page
        window.location.reload();
    }
}

$(document).ready(function() {
    // check periodically if session has expired by getting current page
    // cheap, I know, and terrible for performance---but HEAD gets 500 for some reason with no server logs
    setInterval(checkSessionExpiry, 3600000);

    $("#login-modal__form").on("submit", async function(e) {
        e.preventDefault();

        let formData = new FormData(e.target);
        const respJson = await fetchWrapper(LOGIN_URL, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);

        if (respJson.success) {
            onSamePageLogin();
        }
    });

    $("#logout-link").on("click", async function(e) {
        e.preventDefault();
        const respJson = await fetchWrapper(LOGOUT_URL, {method: "POST"});
    });

    const jQModalLogin = $("#login-modal");
    // differentiate modal vs. non-modal logins for redirect
    jQModalLogin.find("#is_modal").val("true");

    $("#login-modal").on("show.bs.modal", function(e) {
        if (window.location.href.startsWith(LOGIN_URL)) {
            e.preventDefault();
            customFlash("You're already on the login page, you doofus.");
        }
    });

    jQModalLogin.on("shown.bs.modal", function(e) {
        $(e.target).find("#password-input").focus();
    });

    // wipe contents and toggle password visibility off on hide
    jQModalLogin.on("hidden.bs.modal", function(e) {
        const jQInputPassword = $(e.target).find("#password-input");
        jQInputPassword.val("");
        if (jQInputPassword.attr("type") !== "password") {
            togglePasswordVisibility(jQInputPassword.attr("id"), "password-show");
        }
    });
});
