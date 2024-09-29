let commentLoadIntervalId = 0;

// when logging in via modal on a post page/opening a post page as admin and scrolling to the bottom, reload
// comments to make sure we are seeing all of them, and then mark all of them as read
onModalLogin = addToFunction(onModalLogin, function() {
    reloadComments();
});
$(document).ready(function() {
    // we don't load in comments with the rest of the post to avoid long load times; wait until scroll to bottom
    commentLoadIntervalId = setInterval(function() {
        if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 32.0) { // 32 px leeway
            reloadComments();
        }
    }, 1000);
});

// when logging out via modal on a post page, reload comments to clear unread indications (borders)
onModalLogout = addToFunction(onModalLogout, function() {
    reloadComments();
});

async function reloadComments() {
    // make sure we don't keep polling for scroll position if the comments have already been loaded
    if (commentLoadIntervalId) {
        clearInterval(commentLoadIntervalId);
    }

    // refresh the main "leave a comment" form's author autofill; don't do for replies as that should be easy
    // enough manually and could be slow automatically if there's a lot of comments
    if (isUserAuthenticated) {
        $("#leave-a-comment").find("input[name='author']").first().val(VERIFIED_AUTHOR);
    } else {
        $("#leave-a-comment").find("input[name='author']").first().val("");
    }
    
    // get comment count in the heading; JQuery `load()` fragment doesn't seem to work with Jinja variables
    let commentCount = 0;
    let commentUnreadCount = 0;
    let respJson = await fetchWrapper(URL_GET_COMMENT_COUNT, {method: "GET"});
    if (!respJson.errorStatus) {
        commentCount = respJson.count;
    } else if (!respJson.hasHandledError) {
        customFlash("There was an error retrieving comment count :/");
        return;
    }

    // get comment unread count in the heading if admin
    if (isUserAuthenticated) {
        respJson = await fetchWrapper(URL_GET_COMMENT_UNREAD_COUNT, {method: "GET"});
        if (!respJson.errorStatus) {
            commentUnreadCount = respJson.count;
        } else if (respJson.errorStatus !== 429) {
            customFlash("There was an error retrieving comment unread count :/");
            return;
        }
    }

    // reflect comment counts in HTML
    let HTML = `(${commentCount}`;
    if (isUserAuthenticated && commentUnreadCount > 0) {
        HTML += `<span class="auth-true">, <span class="custom-pink">${commentUnreadCount} unread</span></span>`;
    }
    HTML += ")";
    $("#comment-counts").html(HTML);

    // load in comments if there are any
    if (commentCount > 0) {
        respJson = await fetchWrapper(URL_GET_COMMENTS, {method: "GET"});
        if (!respJson.errorStatus) {
            $("#comment-list").html(respJson.html);
        } else if (respJson.errorStatus !== 429) {
            customFlash("There was an error retrieving comments :/");
            return;
        }

        // render timestamps and LaTeX in comments
        flask_moment_render_all();
        MathJax.typesetPromise(["#comment-list"]).then(function() {
            onMathJaxTypeset("#comment-list");
        });

        // apply CSS to comments
        applyGlobalStyles("#comment-list");
        applyPostAndCommentStyles("#comment-list");

        // mark comments as read if admin
        if (isUserAuthenticated) {
            markCommentsAsRead();
        }
    }
}

async function markCommentsAsRead() {
    let respJson = await fetchWrapper(URL_MARK_COMMENTS_AS_READ, {method: "POST"});
    if (respJson.success) {
        updateUnreadCommentsNotifs(); // update notification icon after marking comments as read
    }
}

function onCommentAjaxDone(respJson, e) {
    doAjaxResponseForm(respJson, e);

    if (respJson.success) {
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

function getCommentId(nodeForm) {
    return $(nodeForm).attr("id").match(/\d+/)[0];
}

// no `$(document).ready()` listener attachments for the remaining listeners since comments can be reloaded

/**
 * Reveals fields for adding the comment on clicking a reply button.
 */
$(document).on("submit", ".comment__reply-btn", function(e) {
    e.preventDefault();

    const id = getCommentId(e.target);
    const jQFormAddReply = $(`#comment__add-reply-form-${id}`);
    if (jQFormAddReply.length <= 0) {
        customFlash("haker :3");
        return;
    }

    jQFormAddReply.removeAttr("hidden");
    // insert under right parent; use `name` instead of `id` in case duplicate `id`s throughout all the comments
    // causes issues
    jQFormAddReply.find("[name='parent']").val(id);
    if (isUserAuthenticated) {
        // automatically fill in username if admin
        jQFormAddReply.find("input[name='author']").first().val(VERIFIED_AUTHOR);
        jQFormAddReply.find("input[name='content']").first().focus();
    } else {
        jQFormAddReply.find("input[name='author']").first().focus();
    }
    e.target.setAttribute("hidden", "");

    asteriskRequiredFields();
});

$(document).on("submit", ".ajax-add-comment", async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const respJson = await fetchWrapper(URL_ADD_COMMENT, {method: "POST", body: formData});

    onCommentAjaxDone(respJson, e);
});

$(document).on("submit", ".ajax-delete-comment", async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const respJson = await fetchWrapper(
            URL_DELETE_COMMENT, {method: "POST", body: formData}, {comment_id: getCommentId(e.target)});

    onCommentAjaxDone(respJson, e);
});
