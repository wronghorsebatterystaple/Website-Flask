async function fetchWrapper(urlBase, options, paramsDict=null) {
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

    let urlWithParams = new URL(urlBase);
    if (paramsDict) {
        for (let key in paramsDict) {
            urlWithParams.searchParams.append(key, encodeURIComponent(paramsDict[key]));
        }
    }

    const response = await fetch(urlWithParams, options);
    const responseText = await response.text();
    let responseJson = null;
    try {
        responseJson = JSON.parse(responseText);
    } catch (e) {
        responseJson = null;
    }

    // no error
    if (response.ok && responseJson !== null) {
        doAjaxResponseBase(responseJson);
        return responseJson;
    }

    // some error occurred
    switch(response.status) {
        case 429:
            customFlash("Please slow down :3");
            break;
        case 499:
            // CSRF token expiry; refresh CSRF token and resend the request if this is the case
            let newToken = responseJson.new_csrf_token;
            reloadCSRF(newToken);
            hideAuthElems(); // session must have expired for CSRF expiry

            // resend request with updated CSRF token in FormData (header refresh handled by recursive call)
            if (options.body && options.body instanceof FormData) {
                options.body.set("csrf_token", csrfToken);
            }
            return fetchWrapper(urlBase, options, paramsDict);
            break;
    }

    return { error: true }
}

/**
 * Always-supported JSON keys:
 *     - `relogin`
 *     - `redirect_url`
 *     - `flash_message`
 */
function doAjaxResponseBase(responseJson) {
    if (responseJson.relogin) {
        relogin();
        return;
    }

    if (responseJson.redirect_url) {
        let newUrl = new URL(decodeURIComponent(responseJson.redirect_url));

        // flash message after page load by appending message to URL as custom `flash_message` param
        if (responseJson.flash_message) {
            newUrl.searchParams.append("flash_message", encodeURIComponent(responseJson.flash_message));
        }

        window.location.href = newUrl;
    } else {
        // async flash message
        if (responseJson.flash_message) {
            customFlash(responseJson.flash_message);
        }
    }
}

function doAjaxResponseForm(responseJson, submitEvent) {
    if (!responseJson.redirect_url && responseJson.submission_errors) { 
        let errors = responseJson.submission_errors;
        for (const [fieldName, fieldErrors] of Object.entries(errors)) {
            let elemField = $(submitEvent.target).find(`#${fieldName}-field`)
            elemField.find(`#${fieldName}-input`).addClass("is-invalid");
            elemField.find(".invalid-feedback").text(fieldErrors[0]);
        }
    }
}

function reloadCSRF(newToken) {
    csrfToken = newToken;
    $("input[name='csrf_token']").val(csrfToken); // reload hidden form fields
}
