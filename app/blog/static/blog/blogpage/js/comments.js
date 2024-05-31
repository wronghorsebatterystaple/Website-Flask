// Populate comments' hidden fields for comment addition and deletion
function loadCommentHiddenIds() {
    $(".comment-add-form").find("#post_id").val(POST_ID);

    $(".comment-delete-form").each(function() {
        var id = $(this).attr("id").match(/\d+/)[0];
        $(this).find("#comment_id").val(id);
        $(this).find("#post_id").val(POST_ID);
    });
}

function onCommentReload() {
    flask_moment_render_all();
    loadCommentHiddenIds();

    MathJax.typesetPromise(["#commentlist"]).then(function() { // render any LaTeX in comments
        onMathJaxTypeset("#commentlist");
    });

    $("input[data-confirm-submit][type='submit']").on("click", function() { // refresh listeners
        return confirm("Sanity check");
    });

    applyGlobalStyles("#commentlist");
    applyCommentStyles();
}

function onCommentAjaxDone(responseJSON, e) {
    doBaseAjaxResponse(responseJSON, e);
    if (responseJSON.success) {
        // clear input fields and reset height
        $(e.target).find("*").filter(function() {
            return this.id.match(/.*-input/);
        }).each(function() {
            $(this).val("");
            if ($(this).is("textarea")) {
                adjustTextareaHeight($(this).get(0), false);
            }
        });

        // reload comment section
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

$(document).on("submit", ".ajax-add-comment", async function(e) {
    e.preventDefault();

    var formData = new FormData(e.target);
    const responseJSON = await fetchWrapper(URL_ABS_ADD_COMMENT, {
        method: "POST",
        body: formData
    });

    onCommentAjaxDone(responseJSON, e);
});

$(document).on("submit", ".ajax-delete-comment", async function(e) {
    e.preventDefault();

    var formData = new FormData(e.target);
    const responseJSON = await fetchWrapper(URL_ABS_DELETE_COMMENT, {
        method: "POST",
        body: formData
    });

    onCommentAjaxDone(responseJSON, e);
});
