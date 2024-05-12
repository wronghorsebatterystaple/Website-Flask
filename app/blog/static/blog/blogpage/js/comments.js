// Populate comment's hidden fields for comment addition and deletion
function loadCommentHiddenIds() {
    $(".comment-add-form").find("#post_id").val(postId);

    $(".comment-delete-btn").each(function() {
        var id = $(this).attr("id").match(/\d+/)[0];
        $(this).find("#comment_id").val(id);
        $(this).find("#post_id").val(postId);
    });
}

function onCommentReload() {
    flask_moment_render_all();
    loadCommentHiddenIds();
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

$(document).ready(function() {
    loadCommentHiddenIds();

    // reveal fields for comment on clicking a reply button
    $(".comment-reply-btn").on("submit", function(e) {
        e.preventDefault();

        var id = $(this).attr("id").match(/\d+/)[0];
        var commentReplyForm_elem = $(`#comment-reply-form-${id}`);
        commentReplyForm_elem.removeAttr("hidden");
        commentReplyForm_elem.find("#parent").val(id); // insert under right parent
        commentReplyForm_elem.find("#author-input").focus();
        e.target.setAttribute("hidden", "");

        asteriskRequiredFields();
    });

    $(".ajax-add-comment").on("submit", function(e) {
        e.preventDefault();

        var formData = new FormData($(e.target).get(0));
        $.ajax({
            type: "POST",
            url: endptURL_addComment,
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

    $(".ajax-delete-comment").on("submit", function(e) {
        e.preventDefault();

        var formData = new FormData($(e.target).get(0));
        $.ajax({
            type: "POST",
            url: endptURL_deleteComment,
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
});

