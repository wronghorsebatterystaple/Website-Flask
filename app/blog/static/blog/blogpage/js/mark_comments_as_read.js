$(document).ready(async function() {
    await fetchWrapper(`${getCurrentURLNoQS()}/mark-comments-as-read`, {
        method: "POST",
    });
});
