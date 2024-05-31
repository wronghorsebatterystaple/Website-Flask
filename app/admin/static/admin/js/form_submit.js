$(document).ready(function() {
    $("#main-form").on("submit", async function(e) {
        e.preventDefault();
      
        if (e.originalEvent.submitter.id === "cancel-images-btn") {
            $("#images-input").val("");
            return;
        }

        var formData = new FormData(e.target, e.originalEvent.submitter);
        const responseJSON = await fetchWrapper(window.location.href, {
            method: "POST",
            body: formData
        });

        doBaseAjaxResponse(responseJSON, e);
    });
});
