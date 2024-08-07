const unreadCommentsDropdownBtnIcon_elem = $("#unread-comments-dropdown-btn-icon");

async function checkForNotifs() {
    var notifCount = await populateDropdown();
    if (notifCount > 0) {
        setBellWithNotif();
    } else {
        setBellWithoutNotif();
    }
}

function setBellWithNotif() {
    unreadCommentsDropdownBtnIcon_elem.removeClass("bi-bell");
    unreadCommentsDropdownBtnIcon_elem.addClass("bi-bell-fill");
}

function setBellWithoutNotif() {
    unreadCommentsDropdownBtnIcon_elem.removeClass("bi-bell-fill");
    unreadCommentsDropdownBtnIcon_elem.addClass("bi-bell");
}

async function populateDropdown() {
    const unreadCommentsDropdown_elem = $("#unread-comments-dropdown");
    unreadCommentsDropdown_elem.html("<span class=\"dropdown-item\">Loading…</span>");

    // get posts with unread comments
    const responseJSON = await fetchWrapper(URL_GET_POSTS_WITH_UNREAD_COMMENTS, {
        method: "POST"
    });

    if (responseJSON.error) {
        unreadCommentsDropdown_elem.html("<span class=\"dropdown-item\">! Unable to load posts. Please panic. !</span>");
        return -1;
    }

    if (responseJSON.relogin) {
        relogin();
        unreadCommentsDropdown_elem.html("<span class=\"dropdown-item\">Not so fast :]</span>");
        return -1;
    }

    var postCount = Object.keys(responseJSON).length;
    if (postCount === 0) {
        unreadCommentsDropdown_elem.html("<span class=\"dropdown-item\">There's nothing here :]</span>");
        return postCount;
    }

    var html = "";
    Object.keys(responseJSON).forEach(postTitle => {
        var postURL = responseJSON[postTitle].url;
        var postUnreadCount = responseJSON[postTitle].unread_count;
        html += `<a class="dropdown-item" href="${postURL}"><span class="custom-pink">(${postUnreadCount})</span> ${postTitle}</a>`;
    });
    unreadCommentsDropdown_elem.html(html);

    return postCount;
}

/**
 * Aligns dropdown to the left of its button (since it's on the right of the screen; we don't want overflow).
 */
function alignDropdownLeftwards(records) {
    const dropdown_dom = records[0].target;
    var offset = dropdown_dom.offsetWidth - document.querySelector("#unread-comments-dropdown-btn").offsetWidth;
    document.documentElement.style.setProperty("--unread-comments-dropdown-left", `-${offset}px`);
}

$(document).ready(function() {
    // observe for changes in innerHTML to re-align the dropdown leftwards
    const mutationObserver = new MutationObserver(alignDropdownLeftwards);
    mutationObserver.observe(document.querySelector("#unread-comments-dropdown"), {
        childList: true
    });

    // refresh notifications on click
    $("#unread-comments-dropdown-btn").on("click", function() {
        checkForNotifs();
    });
});
