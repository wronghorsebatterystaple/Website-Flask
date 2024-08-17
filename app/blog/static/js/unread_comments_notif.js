const elemUnreadCommentsDropdownBtnIcon = $("#unread-comments-notif-btn-icon");

/* When logging in via modal on a `blog.` page/opening a `blog.` page as admin, check for notifications */
onModalLogin = addToFunction(onModalLogin, function() {
    updateUnreadCommentsNotifs();
});
$(document).ready(function() {
    if (isUserAuthenticated) {
        updateUnreadCommentsNotifs();
    }
});

async function updateUnreadCommentsNotifs() {
    let notifCount = await updateUnreadCommentsDropdown();
    if (notifCount > 0) {
        setBellWithNotif();
    } else {
        setBellWithoutNotif();
    }
}

function setBellWithNotif() {
    elemUnreadCommentsDropdownBtnIcon.removeClass("bi-bell");
    elemUnreadCommentsDropdownBtnIcon.addClass("bi-bell-fill");
}

function setBellWithoutNotif() {
    elemUnreadCommentsDropdownBtnIcon.removeClass("bi-bell-fill");
    elemUnreadCommentsDropdownBtnIcon.addClass("bi-bell");
}

async function updateUnreadCommentsDropdown() {
    const elemUnreadCommentsDropdown = $("#unread-comments-dropdown");

    // get posts with unread comments
    elemUnreadCommentsDropdown.html("<span class=\"dropdown-item\">Loading…</span>");
    const responseJson = await fetchWrapper(URL_GET_POSTS_WITH_UNREAD_COMMENTS, { method: "POST" });

    if (responseJson.error) {
        elemUnreadCommentsDropdown.html("<span class=\"dropdown-item\">Unable to load posts ;-;</span>");
        return -1;
    }

    if (responseJson.relogin) {
        elemUnreadCommentsDropdown.html("<span class=\"dropdown-item\">Not so fast :]</span>");
        return -1;
    }

    let postCount = Object.keys(responseJson).length;
    if (postCount === 0) {
        elemUnreadCommentsDropdown.html("<span class=\"dropdown-item\">There's nothing here :]</span>");
        return postCount;
    }

    let html = "";
    Object.keys(responseJson).forEach(postTitle => {
        let postUrl = responseJson[postTitle].url;
        let postUnreadCount = responseJson[postTitle].unread_count;
        html += `<a class="dropdown-item" href="${postUrl}"><span class="custom-pink">(${postUnreadCount})</span> ${postTitle}</a>`;
    });
    elemUnreadCommentsDropdown.html(html);

    return postCount;
}

/**
 * Aligns dropdown to the left of its button (since it's on the right of the screen; we don't want overflow).
 */
function alignDropdownLeftwards(records) {
    const domDropdown = records[0].target;
    let offset = domDropdown.offsetWidth - document.querySelector("#unread-comments-notif-btn").offsetWidth;
    document.documentElement.style.setProperty("--unread-comments-dropdown-left", `-${offset}px`);
}

$(document).ready(function() {
    // observe for changes in innerHTML to re-align the dropdown leftwards
    const mutationObserver = new MutationObserver(alignDropdownLeftwards);
    mutationObserver.observe(document.querySelector("#unread-comments-dropdown"), {
        childList: true
    });

    // refresh notifications on click
    $("#unread-comments-notif-btn").on("click", function() {
        updateUnreadCommentsNotifs();
    });
});
