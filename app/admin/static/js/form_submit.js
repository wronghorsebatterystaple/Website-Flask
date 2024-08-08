$(document).ready(function() {
    $("#main-form").on("submit", async function(e) {
        e.preventDefault();
      
        const submitter_elem = $(e.originalEvent.submitter);
        if (submitter_elem.is("[data-no-submit]")) {
            switch (submitter_elem.attr("id")) {
                case "cancel-image-uploads-btn":
                    $("#images-input").val("");
                    break;
                case "cancel-delete-images-btn":
                    $("#delete_images-input").val("");
                    break;
            }
            return;
        }

        var formData = new FormData(e.target, e.originalEvent.submitter);
        const responseJSON = await fetchWrapper(window.location.href, { method: "POST", body: formData });

        doBaseAjaxResponse(responseJSON, e);
    });
});
