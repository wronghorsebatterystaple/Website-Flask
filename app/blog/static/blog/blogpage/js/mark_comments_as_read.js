$(document).ready(async function() {
    await fetchWrapper(`${getCurrentURLNoQS()}/mark-comments-as-read`, {
        method: "POST",
    });

    checkForNotifs(); // update notification icon after marking comments as read
});
