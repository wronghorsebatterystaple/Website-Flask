// Populate comments' hidden fields for comment addition and deletion
function loadCommentHiddenIds() {
    $(".comment-add-form").find("#post_id").val(postId);

    $(".comment-delete-form").each(function() {
        var id = $(this).attr("id").match(/\d+/)[0];
        $(this).find("#comment_id").val(id);
        $(this).find("#post_id").val(postId);
    });
}

function onCommentReload() {
    flask_moment_render_all();
    loadCommentHiddenIds();
    MathJax.typeset(["#commentlist"]); // render any LaTeX in comments
    $("input[data-confirm-submit][type='submit']").on("click", function() { // refresh listeners
        return confirm("Sanity check");
    });
    applyGlobalStyles("#commentlist");
    applyCommentStyles();
}

function onCommentAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);

    if (response.success) {
        $(e.target).find("*").filter(function() {
            return this.id.match(/.*-input/);
        }).each(function() {
            // clear input fields and reset height
            $(this).val("");
            if ($(this).is("textarea")) {
                adjustTextareaHeight($(this).get(0), false);
            }
        });
        $("#commentlist").load(window.location.href + " #commentlist > *", onCommentReload);
    }
}

$(document).ready(loadCommentHiddenIds);

// No $(document).ready listener attachments for the remaining listeners since comments can be reloaded with load()
// Reveal fields for comment on clicking a reply button
$(document).on("submit", ".comment-reply-form", function(e) {
    e.preventDefault();

    var id = $(this).attr("id").match(/\d+/)[0];
    var commentReplyAddForm_elem = $(`#comment-reply-add-form-${id}`);
    commentReplyAddForm_elem.removeAttr("hidden");
    commentReplyAddForm_elem.find("#parent").val(id); // insert under right parent
    commentReplyAddForm_elem.find("#author-input").focus();
    e.target.setAttribute("hidden", "");

    asteriskRequiredFields();
});

$(document).on("submit", ".ajax-add-comment", function(e) {
    e.preventDefault();

    var formData = new FormData($(e.target).get(0));
    $.ajax({
        type: "POST",
        url: URL_addComment,
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
        handleAjaxErrors(jqXHR, formData, e, self, onCommentAjaxDone);
    });
});

$(document).on("submit", ".ajax-delete-comment", function(e) {
    e.preventDefault();

    var formData = new FormData($(e.target).get(0));
    $.ajax({
        type: "POST",
        url: URL_deleteComment,
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
        handleAjaxErrors(jqXHR, formData, e, self, onCommentAjaxDone);
    });
});

