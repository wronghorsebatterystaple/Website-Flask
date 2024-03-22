// Asynchronously reveal fields for comment on clicking a reply button, and don't send POST at all
$(document).on("submit", ".reply-btn", function(e) {
    e.preventDefault();

    var id = $(this).attr("id").match(/\d+/)[0] // get matching id number
    $(`#reply-form-${id}`).removeAttr("hidden");
    $(`#reply-form-${id}`).find("#parent").attr("value", id); // insert under right parent
});

// Use Ajax to update page on comment addition without refreshing and going back to top
$(document).on("submit", ".post-commentform-form", function(e) {
    e.preventDefault();

    $.ajax({
        type: "POST",
        url: window.location.pathname + window.location.search,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(formToJSON($(this))),
        dataType: "json",
    })
    .done(function(response) {
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

            if (response.success) {
                $("#commentlist").load(window.location.href + " #commentlist > *");
            }
        }
    });
});
