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
    if (response.redirect_uri) {
        var newURI = response.redirect_uri;
        if (response.flash_message) {
            newURI += `?flash=${encodeURIComponent(response.flash_message)}`;
        }
        window.location.href = newURI;
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
