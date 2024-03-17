/*
 * Util function that converts <form> element and its data to a JSON for Ajax.
 */
function formToJSON(formObj) {
    var array = formObj.serializeArray();
    var json = {};
  
    $.map(array, function(n, i) {
        json[n["name"]] = n["value"];
    });
  
    return json;
}


/*
 * Add CSRF token to headers
 */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrf_token);
      }
    }
});


/*
 * Use Ajax to intercept form submissions, pass to Flask manually, and process the response
 * so we can have asynchronous flash()ing/input validation messages on errored response from Flask.
 */
$("#form").submit(function(e) {
    e.preventDefault();
  
    var data = formToJSON($(this))
    // send customid in POST request to differentiate multiple submit buttons in routes.py
    var submit_button_customid = $(e.originalEvent.submitter).attr("data-submit-customid")
    if (submit_button_customid) { // only proceed if this attribute is defined
        data[submit_button_customid] = true;
    }
  
    $.ajax({
        type: "POST",
        url: window.location.pathname + window.location.search,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(data),
        dataType: "json",
    })
    .done(function(response) {
        if (response.redirect) {
            window.location.href = response.redirect_url;
        } else {
            if (response.invalid_submission) { 
                // dynamically populate input validation message elements (from bootstrap_wtf.html)
                // `errors`' keys, returned from Flask as form.errors, are Jinja's field.name
                // which we make sure to match in bootstrap_wtf.html when assigning id attributes
                errors = response.submission_errors;
                Object.keys(errors).forEach((field_name) => {
                    var field_elem = $("#form").find(`#${field_name}-field`)
                    field_elem.find(`#${field_name}-input`).addClass("is-invalid");
                    field_elem.find(".invalid-feedback").text(errors[field_name][0]);
                });
            } else {
                custom_flash(response.flash);
            }
        }
    });
});


/*
 * Remove invalid input highlighting and error message when user inputs into field.
 */
$(".form-control").on("input", function() {
    if ($(this).hasClass("is-invalid")) {
        $(this).removeClass("is-invalid");
        $(this).siblings(".invalid-feedback").text(""); // this apparently also hides the div
    }
});
