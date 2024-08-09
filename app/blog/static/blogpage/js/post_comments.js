let commentLoadIntervalId;

/* When logging in via modal on a post page/opening a post page as admin and scrolling to the bottom, reload
 * comments to make sure we are seeing all the comments, and then mark all of them as read */
onModalLogin = addToFunction(onModalLogin, function() {
    reloadComments();
});
$(document).ready(function() {
    // we don't load in comments with the rest of the post to avoid long initial load times
    commentLoadIntervalId = setInterval(function() {
        if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 32.0) { // 32 px leeway
            reloadComments();
        }
    }, 1000);
});

/* When logging out via modal on a post page, reload comments to clear unread indications (borders) */
onModalLogout = addToFunction(onModalLogout, function() {
    reloadComments();
});

async function reloadComments() {
    // refresh the comment counts in the heading; JQuery `load()` fragment doesn't seem to work with Jinja variables
    let commentCount = 0;
    let commentUnreadCount = 0;
    let responseJSON = await fetchWrapper(URL_GET_COMMENT_COUNT, { method: "POST" });
    commentCount = responseJSON.count;
    if (isUserAuthenticated) {
        responseJSON = await fetchWrapper(URL_GET_COMMENT_UNREAD_COUNT, { method: "POST" });
        commentUnreadCount = responseJSON.count;
    }

    let HTML = `(${commentCount}`;
    if (isUserAuthenticated && commentUnreadCount > 0) {
        HTML += `<span class="auth-true">, <span class="custom-pink">${commentUnreadCount} unread</span></span>`;
    }
    HTML += ")";
    $("#comment-list-heading-counts").html(HTML);
    
    // load in comments
    responseJSON = await fetchWrapper(URL_GET_COMMENTS, { method: "GET" });
    $("#comment-list").html(responseJSON.html);

    // make sure we don't keep polling for scroll position if the comments have already been loaded
    if (commentLoadIntervalId) {
        clearInterval(commentLoadIntervalId);
    }

    // apply CSS to comments
    applyGlobalStyles("#comment-list");
    applyCommentStyles();

    // render timestamps and LaTeX in comments
    flask_moment_render_all();
    MathJax.typesetPromise(["#comment-list"]).then(function() {
        onMathJaxTypeset("#comment-list");
    });

    if (isUserAuthenticated) {
        markCommentsAsRead();
    }
}

async function markCommentsAsRead() {
    await fetchWrapper(URL_MARK_COMMENTS_AS_READ, { method: "POST" });
    updateUnreadCommentsNotifs(); // update notification icon after marking comments as read
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

        // reload comment section to show changes asynchronously
        reloadComments();
    }
}

function getCommentId(domForm) {
    return $(domForm).attr("id").match(/\d+/)[0];
}

/* No $(document).ready listener attachments for the remaining listeners since comments can be reloaded */

$(document).on("click", "input[data-confirm-submit][type='submit']", function() {
    return confirm("Sanity check");
});

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
