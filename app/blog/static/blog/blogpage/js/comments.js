var digits_reg = /\d+/;

// Asynchronously reveal fields for comment on clicking a reply button, and don't send POST at all
$(document).on("submit", ".comment-reply-btn", function(e) {
    e.preventDefault();

    var id = $(this).attr("id").match(digits_reg)[0];
    $(`#comment-reply-form-${id}`).removeAttr("hidden");
    $(`#comment-reply-form-${id}`).find("#parent").val(id);
    e.target.setAttribute("hidden", "");

    asteriskRequiredFields();
});

// Asynchronously populate comment id hidden fields for comment deletion
function loadDeleteButtonIDs() {
    $(".comment-delete-btn").each(function() {
        var id = $(this).attr("id").match(digits_reg)[0];
        $(this).find("#id").val(id);
    });
}
$(document).ready(loadDeleteButtonIDs)

// Use Ajax to update page on comment addition/deletion without refreshing and going back to top
function onCommentReload() {
    flask_moment_render_all();
    loadDeleteButtonIDs();
}

$(document).on("submit", ".comment-ajax", function(e) {
    e.preventDefault();

    var formData = new FormData($(e.target).get(0), $(e.originalEvent.submitter).get(0));
    $.ajax({
        type: "POST",
        url: window.location.pathname + window.location.search,
        data: formData,
        processData: false,
        contentType: false,
        dataType: "json"
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

            if (response.success) { // clear fields and reload comments on success
                $(e.target).find("*").filter(function() {
                    return this.id.match(/.*-input/);
                }).val("");
                $("#commentlist").load(window.location.href + " #commentlist > *", onCommentReload);
            }
        }
    });
});
