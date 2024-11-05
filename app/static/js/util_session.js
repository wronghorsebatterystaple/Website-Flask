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

// this can't do anything to prevent users from just closing the modal
// my principle is that letting an expired session simply continue viewing a restricted page with no ability to
// interact (since it will always ask for modal and not do anything) is not a huge deal
// (if I forgot to log out at public computer or something then we have a LOT of other problems)
function relogin() {
    // don't do `onSamePageLogout()` to change visuals either since there's an infinite loop with `reloadComments()`
    // that I don't wanna fix
    customFlash("Your session has expired. Please log in again ^^");
    $("#login-modal").modal("show");
}

$(document).ready(function() {
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
    // differentiate modal vs. non-modal logins for redirecting back
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
