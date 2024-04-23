function handleCustomErrors(jqXHR, formData, e, self, doneFunc) {
    if (jqXHR.status === 499) {
        reloadCSRF(jqXHR.responseText);
        hideAuthElems(); // session must have expired for CSRF expired error

        if (!$(e.target).hasClass("login-req-form")) {
            formData.set("csrf_token", csrf_token)
            $.ajax(self).done(function(response) {
                doneFunc(response, e);
            });
        } else { 
            customFlash("Your session has expired. Please log in again.");
            relogin();
        }
    }
}

