function getCommentId(domForm) {
    return $(domForm).attr("id").match(/\d+/)[0];
}

function onCommentReload() {
    flask_moment_render_all();

    MathJax.typesetPromise(["#comment-list"]).then(function() {             // render LaTeX in comments
        onMathJaxTypeset("#comment-list");
    });

    $("input[data-confirm-submit][type='submit']").on("click", function() { // refresh listeners
        return confirm("Sanity check");
    });

    applyGlobalStyles("#comment-list");
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
        $("#comment-list").load(window.location.href + " #comment-list > *", onCommentReload);
    }
}

// no $(document).ready listener attachments for the remaining listeners since comments can be reloaded with load()

/*
 * Reveals fields for adding the comment on clicking a reply button.
 */
$(document).on("submit", ".comment-reply-form", function(e) {
    e.preventDefault();

    let id = getCommentId(e.target);
    let elemCommentReplyAddForm = $(`#comment-reply-add-form-${id}`);
    elemCommentReplyAddForm.removeAttr("hidden");
    elemCommentReplyAddForm.find("#parent").val(id); // insert under right parent
    elemCommentReplyAddForm.find("#author-input").focus();
    e.target.setAttribute("hidden", "");

    asteriskRequiredFields();
});

$(document).on("submit", ".ajax-add-comment", async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const responseJSON = await fetchWrapper(
            `${getCurrentURLNoQS()}/add-comment`,
            { method: "POST", body: formData });

    onCommentAjaxDone(responseJSON, e);
});

$(document).on("submit", ".ajax-delete-comment", async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const responseJSON = await fetchWrapper(
            `${getCurrentURLNoQS()}/delete-comment`,
            { method: "POST", body: formData },
            { comment_id: getCommentId(e.target) });

    onCommentAjaxDone(responseJSON, e);
});
