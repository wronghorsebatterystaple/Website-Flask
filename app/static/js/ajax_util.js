async function fetchWrapper(baseURL_abs, options, paramsDict=null) {
    if (!options) {
        options = {};
    }
    if (!options.headers) {
        options.headers = {};
    }
    options.headers["X-CSRFToken"] = csrfToken;
    options.headers["Accept"] = "application/json";
    options.credentials = "include";
    options.mode = "cors";

    let URLWithParams_abs = new URL(baseURL_abs);
    if (paramsDict) {
        for (let key in paramsDict) {
            URLWithParams_abs.searchParams.append(key, encodeURIComponent(paramsDict[key]));
        }
    }

    const response = await fetch(URLWithParams_abs, options);
    const responseText = await response.text();
    let responseJSON;
    try {
        responseJSON = JSON.parse(responseText);
    } catch (e) {
        responseJSON = null;
    }

    // no error
    if (response.ok && responseJSON !== null) {
        doAjaxResponseBase(responseJSON);
        return responseJSON;
    }

    // some error occurred
    switch(response.status) {
        case 429:
            customFlash("Please slow down :3");
            break;
        case 499:
            // CSRF token expiry; refresh CSRF token and resend the request if this is the case
            let newToken = responseJSON.new_csrf_token;
            reloadCSRF(newToken);
            hideAuthElems(); // session must have expired for CSRF expiry

            // resend request with updated CSRF token in FormData (header refresh handled by recursive call)
            if (options.body && options.body instanceof FormData) {
                options.body.set("csrf_token", csrfToken);
            }
            return fetchWrapper(baseURL_abs, options, paramsDict);
            break;
    }

    return { error: true }
}

function doAjaxResponseBase(responseJSON) {
    if (responseJSON.relogin) {
        relogin();
        return;
    }

    if (responseJSON.redirect_url) {
        let newURL = new URL(decodeURIComponent(responseJSON.redirect_url));

        // flash message after page load by appending message to URL as custom `flash_message` param
        if (responseJSON.flash_message) {
            newURL.searchParams.append("flash_message", encodeURIComponent(responseJSON.flash_message));
        }

        window.location.href = newURL;
    } else {
        // async flash message
        if (responseJSON.flash_message) {
            customFlash(responseJSON.flash_message);
        }
    }
}

function doAjaxResponseForm(responseJSON, submitEvent) {
    if (!responseJSON.redirect_url && responseJSON.submission_errors) { 
        let errors = responseJSON.submission_errors;
        Object.keys(errors).forEach((field_name) => {
            let elemField = $(submitEvent.target).find(`#${field_name}-field`)
            elemField.find(`#${field_name}-input`).addClass("is-invalid");
            elemField.find(".invalid-feedback").text(errors[field_name][0]);
        });
    }
}

function reloadCSRF(newToken) {
    csrfToken = newToken;
    $("input[name='csrf_token']").val(csrfToken); // reload hidden form fields
}
