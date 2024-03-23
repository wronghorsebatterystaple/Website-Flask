// Use Ajax to intercept form submissions, pass to Flask manually, and process the response
// so we can have asynchronous flash()ing/input validation messages on errored response from Flask.
$(document).on("submit", "form", function(e) {
    e.preventDefault();
  
    var formData = new FormData($(this).get(0), $(e.originalEvent.submitter).get(0));
    $.ajax({
        type: "POST",
        url: window.location.pathname + window.location.search,
        data: formData,
        processData: false,
        contentType: false,
        dataType: "json",
    })
    .done(function(response) {
        if (response.redirect_uri) {
            var newURI = response.redirect_uri;
            if (response.flash_message) { // put flash into query string to render after load
                newURI += `?flash=${encodeURIComponent(response.flash_message)}`;
            }
            window.location.href = newURI;
        } else {
            // immediately flash if no redirect (async)
            if (response.flash_message) {
                customFlash(response.flash_message);
            }
            
            if (response.submission_errors) { 
                // dynamically populate input validation message elements (from bootstrap_wtf.html)
                // `errors`' keys, returned from Flask as form.errors, are Jinja's field.name
                // which we make sure to match in bootstrap_wtf.html when assigning id attributes
                errors = response.submission_errors;
                Object.keys(errors).forEach((field_name) => {
                    var field_elem = $(e.target).find(`#${field_name}-field`)
                    field_elem.find(`#${field_name}-input`).addClass("is-invalid");
                    field_elem.find(".invalid-feedback").text(errors[field_name][0]);
                });
            }
        }
    });
});
