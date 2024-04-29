// Reveal fields for comment on clicking a reply button
$(document).on("submit", ".comment-reply-btn", function(e) {
    e.preventDefault();

    var id = $(this).attr("id").match(/\d+/)[0];
    var commentReplyForm_elem = $(`#comment-reply-form-${id}`);
    commentReplyForm_elem.removeAttr("hidden");
    commentReplyForm_elem.find("#parent").val(id); // insert under right parent
    commentReplyForm_elem.find("#author-input").focus();
    e.target.setAttribute("hidden", "");

    asteriskRequiredFields();
});

// Populate comment id hidden fields for comment deletion
function loadDeleteButtonIDs() {
    $(".comment-delete-btn").each(function() {
        var id = $(this).attr("id").match(/\d+/)[0];
        $(this).find("#id").val(id);
    });
}
$(document).ready(loadDeleteButtonIDs)

function onCommentReload() {
    flask_moment_render_all();
    loadDeleteButtonIDs();
    MathJax.typeset(["#commentlist"]); // render any LaTeX in comments
}

function onCommentAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);

    if (response.success) {
        $(e.target).find("*").filter(function() {
            return this.id.match(/.*-input/);
        }).val(""); // clear
        $("#commentlist").load(window.location.href + " #commentlist > *", onCommentReload);
    }
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
        onCommentAjaxDone(response, e);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        var self = this;
        handleCustomErrors(jqXHR, formData, e, self, onCommentAjaxDone);
    });
});
