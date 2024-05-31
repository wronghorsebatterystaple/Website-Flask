function reloadCSRF(newToken) {
    csrf_token = newToken;
    $("input[name='csrf_token']").val(csrf_token); // reload hidden form fields
}

async function fetchWrapper(URL, options, paramsDict=null) {
    if (!options) {
        options = {};
    }
    if (!options.headers) {
        options.headers = {};
    }
    options.headers["X-CSRFToken"] = csrf_token;
    options.headers["Accept"] = "application/json";
    options.credentials = "include";

    var URLWithParams = URL;
    if (paramsDict) {
        URLWithParams += "?" + new URLSearchParams(paramsDict);
    }
    var response = await fetch(URLWithParams, options);

    // catch HTTP errors, including custom errors, and make sure we don't try to .json() an errored response
    if (!response.ok) {
        console.log(response.status);
        if (response.status === 499) {
            reloadCSRF(response.body);
            hideAuthElems(); // session must have expired for CSRF expiry

            // resend request recursively with updated CSRF token
            if (options.body && options.body instanceof FormData) {
                options.body.set("csrf_token", csrf_token);
            }
            return fetchWrapper(URL, options, paramsDict);
        }

        if (response.status === 429) {
            customFlash("Please slow down :3");
        }
        return {error: true}
    }

    return response.json();
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrf_token);
      }
    }
});

$.ajaxPrefilter(function(options) {
    options.xhrFields = {withCredentials: true};
});

function processStandardAjaxResponse(responseJSON, e) {
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
