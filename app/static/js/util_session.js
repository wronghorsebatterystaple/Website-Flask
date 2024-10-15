let onSamePageLogin = function() {
    isUserAuthenticated = true;
    $("#login-modal").modal("hide");
    $(".show-when-logged-out").attr("hidden", "");
    $(".show-when-logged-in").removeAttr("hidden");
};

let onSamePageLogout = function() {
    isUserAuthenticated = false;
    $(".show-when-logged-in").attr("hidden", "");
    $(".show-when-logged-out").removeAttr("hidden");
};

$(document).ready(function() {
    const jQModalLogin = $("#login-modal");
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

    $("#login-modal__form").on("submit", async function(e) {
        e.preventDefault();

        let formData = new FormData(e.target);
        const respJson = await fetchWrapper(LOGIN_URL, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);

        if (respJson.success) {
            onSamePageLogin();
        }
    });

    $("#login-modal").on("show.bs.modal", function(e) {
        if (window.location.href.startsWith(LOGIN_URL)) {
            e.preventDefault();
            customFlash("You're already on the login page, you doofus.");
        }
    });
});
