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

function processStandardAjaxResponse(response, e) {
    if (response.relogin) {
        relogin();
        return;
    }

    if (response.redirect_url_abs) {
        var newURL = new URL(decodeURIComponent(response.redirect_url_abs));
        if (response.flash_message) {
            newURL.searchParams.append("flash", encodeURIComponent(response.flash_message));
        }
        window.location.href = newURL;
    } else {
        if (response.flash_message) {
            customFlash(response.flash_message);
        }
        
        if (response.submission_errors) { 
            errors = response.submission_errors;
            Object.keys(errors).forEach((field_name) => {
                var field_elem = $(e.target).find(`#${field_name}-field`)
                field_elem.find(`#${field_name}-input`).addClass("is-invalid");
                field_elem.find(".invalid-feedback").text(errors[field_name][0]);
            });
        }
    }
}
