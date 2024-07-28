$(document).ready(function() {
    $("#unread-comments-dropdown-btn").on("click", async function() {
        const unreadCommentsDropdown_elem = $("#unread-comments-dropdown");
        unreadCommentsDropdown_elem.html("");

        const responseJSON = await fetchWrapper(URL_ABS_POST_GET_POSTS_WITH_UNREAD_COMMENTS, {
            method: "POST"
        });

        if (responseJSON.error) {
            unreadCommentsDropdown_elem.append("<p>! Unable to load posts. Please panic. !</p>");
            return;
        }

        if (Object.keys(responseJSON).length === 0) {
            unreadCommentsDropdown_elem.append("<p>There's nothing here :]</p>");
            return;
        }

        Object.keys(responseJSON).forEach(postTitle => {
            unreadCommentsDropdown_elem.append(`<div><a href="${responseJSON[postTitle]}">${postTitle}</a></div>`);
        });
    });
});
