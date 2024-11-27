$(document).ready(function() {
    $("#cancel_image_uploads-input").on("click", function() {
        $("#images-input").val("");
    });

    $("#cancel_delete_images-input").on("click", function() {
        $("#delete_images-input").val("");
    });

    $("#delete_post-input").on("click", async function() {
        const respJson = await fetchWrapper(window.location.href, {method: "DELETE"});
        doAjaxResponseForm(respJson, e);
    });
});
