$(document).ready(async function() {
    await fetchWrapper(`${getCurrentURLNoQS()}/mark-comments-as-read`, {
        method: "POST",
    });

    setBellNotifStatus(); // update notification icon after marking comments as read
});
