function reloadCSRF(newToken) {
    csrf_token = newToken;
    $("input[name='csrf_token']").val(csrf_token); // reload hidden form fields
}

async function fetchWrapper(baseURL, options, paramsDict=null) {
    if (!options) {
        options = {};
    }
    if (!options.headers) {
        options.headers = {};
    }
    options.headers["X-CSRFToken"] = csrf_token;
    options.headers["Accept"] = "application/json";
    options.credentials = "include";
    options.mode = "cors";

    var URLWithParams = new URL(baseURL);
    if (paramsDict) {
        for (var key in paramsDict) {
            URLWithParams.searchParams.append(key, encodeURIComponent(paramsDict[key]));
        }
    }

    var response = await fetch(URLWithParams, options);

    // catch HTTP errors, including custom errors, and make sure we don't try to .json() an errored response
    if (!response.ok) {
        if (response.status === 499) {
            var newToken = await response.text();
            reloadCSRF(newToken);
            hideAuthElems(); // session must have expired for CSRF expiry

            // resend request with updated CSRF token in FormData (header refresh handled by recursive call)
            if (options.body && options.body instanceof FormData) {
                options.body.set("csrf_token", csrf_token);
            }
            return fetchWrapper(baseURL, options, paramsDict);
        }

        if (response.status === 429) {
            customFlash("Please slow down :3");
        }
        return {error: true}
    }

    return response.json();
}

function doBaseAjaxResponse(responseJSON, e) {
    if (responseJSON.error) {
        return;
    }

    if (responseJSON.relogin) {
        relogin();
        return;
    }

    if (responseJSON.redirect_url_abs) {
        var newURL = new URL(decodeURIComponent(responseJSON.redirect_url_abs));
        if (responseJSON.flash_message) {
            newURL.searchParams.append("flash", encodeURIComponent(responseJSON.flash_message));
        }
        window.location.href = newURL;
    } else {
        if (responseJSON.flash_message) {
            customFlash(responseJSON.flash_message);
        }
        
        if (responseJSON.submission_errors) { 
            errors = responseJSON.submission_errors;
            Object.keys(errors).forEach((field_name) => {
                var field_elem = $(e.target).find(`#${field_name}-field`)
                field_elem.find(`#${field_name}-input`).addClass("is-invalid");
                field_elem.find(".invalid-feedback").text(errors[field_name][0]);
            });
        }
    }
}
