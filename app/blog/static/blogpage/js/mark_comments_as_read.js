$(document).ready(async function() {
    await fetchWrapper(URL_MARK_COMMENTS_AS_READ, { method: "POST" });
    checkForNotifs(); // update notification icon after marking comments as read
});
