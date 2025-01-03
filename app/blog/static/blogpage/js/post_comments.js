let commentLoadIntervalId = 0;

// when logging in via modal on a post page/opening a post page as admin and scrolling to the bottom, reload
// comments to make sure we are seeing all of them, and then mark all of them as read
onSamePageLogin = addToFunction(onSamePageLogin, function() {
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

async function reloadComments() {
    const isUserAuthenticated = await IS_USER_AUTHENTICATED();

    // make sure we don't keep polling for scroll position if the comments have already been loaded
    if (commentLoadIntervalId) {
        clearInterval(commentLoadIntervalId);
    }

    // refresh the main "leave a comment" form's author autofill; don't do for replies as that should be easy
    // enough manually and could be slow automatically if there's a lot of comments
    $("#leave-a-comment").find("input[name='author']").first().val(isUserAuthenticated ? VERIFIED_AUTHOR : "");
    
    // get comment count in the heading; JQuery `load()` fragment doesn't seem to work with Jinja variables
    let commentCount = 0;
    let commentUnreadCount = 0;
    let respJson = await fetchWrapper(GET_COMMENT_COUNT_URL, {method: "GET"});
    if (!respJson.errorStatus) {
        commentCount = respJson.count;
    } else if (!respJson.hasHandledError) {
        customFlash("There was an error retrieving comment count :/");
        return;
    }

    // get comment unread count in the heading if admin
    if (isUserAuthenticated) {
        respJson = await fetchWrapper(GET_COMMENT_UNREAD_COUNT_URL, {method: "GET"});
        if (!respJson.errorStatus) {
            commentUnreadCount = respJson.count;
        } else if (respJson.errorStatus !== 429) {
            customFlash("There was an error retrieving comment unread count :/");
            return;
        }
    }

    // add comment counts to HTML
    let HTML = `(${commentCount}`;
    if (isUserAuthenticated && commentUnreadCount > 0) {
        HTML +=
            '<span class="show-when-logged-in">' +
              `, <span class="custom-pink-deep-light">${commentUnreadCount} unread</span>` +
            "</span>";
    }
    HTML += ")";
    $("#comment-counts").html(HTML);

    // load in comments if there are any
    if (commentCount === 0) {
        $("#comment-list").html("");
    } else {
        respJson = await fetchWrapper(GET_COMMENTS_URL, {method: "GET"});
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
    let respJson = await fetchWrapper(MARK_COMMENTS_AS_READ_URL, {method: "POST"});
    if (respJson.success) {
        updateUnreadComments();
    }
}

function onCommentAjaxDone(respJson, e) {
    doAjaxResponseForm(respJson, e);

    if (respJson.success) {
        // clear input fields and reset height
        $(e.target).find("*").filter(function() {
            return this.id.match(/.*-input/);
        }).each(function() {
            if ($(this).is("textarea")) {
                $(this).val("");
                adjustTextareaHeight($(this).get(0), false);
            }
        });

        // reload comment section to show changes
        reloadComments();
    }
}

function getCommentId(nodeForm) {
    return $(nodeForm).attr("id").match(/\d+/)[0];
}

// no `$(document).ready()` listener attachments for the remaining listeners since comments can be reloaded

// reveals fields for adding the comment on clicking a reply button
$(document).on("submit", ".comment__reply-btn", async function(e) {
    e.preventDefault();

    const id = getCommentId(e.target);
    const jQFormAddReply = $(`#comment__add-reply-form-${id}`);
    if (jQFormAddReply.length === 0) {
        customFlash("haker :3");
        return;
    }

    jQFormAddReply.removeAttr("hidden");
    // insert under right parent; use `name` instead of `id` in case duplicate `id`s in comments causes issues
    jQFormAddReply.find("[name='parent']").val(id);
    if (await IS_USER_AUTHENTICATED()) {
        // automatically fill in username if admin
        jQFormAddReply.find("input[name='author']").first().val(VERIFIED_AUTHOR);
        jQFormAddReply.find("input[name='content']").first().focus();
    } else {
        jQFormAddReply.find("input[name='author']").first().focus();
    }
    e.target.setAttribute("hidden", "");
});

$(document).on("submit", ".ajax-add-comment", async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const respJson = await fetchWrapper(ADD_COMMENT_URL, {method: "POST", body: formData});

    onCommentAjaxDone(respJson, e);
});

$(document).on("submit", ".ajax-delete-comment", confirmBtn(async function(e) {
    e.preventDefault();

    let formData = new FormData(e.target);
    const respJson = await fetchWrapper(
        DELETE_COMMENT_URL, {method: "POST", body: formData}, {comment_id: getCommentId(e.target)}
    );
    onCommentAjaxDone(respJson, e);
}));
