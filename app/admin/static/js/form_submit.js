$(document).ready(function() {
    $("#main-form").on("submit", async function(e) {
        e.preventDefault();
      
        const elemSubmitter = $(e.originalEvent.submitter);
        if (elemSubmitter.is("[data-no-submit]")) {
            switch (elemSubmitter.attr("id")) {
                case "cancel-image-uploads-btn":
                    $("#images-input").val("");
                    break;
                case "cancel-delete-images-btn":
                    $("#delete_images-input").val("");
                    break;
            }
            return;
        }

        let formData = new FormData(e.target, e.originalEvent.submitter);
        const responseJSON = await fetchWrapper(window.location.href, { method: "POST", body: formData });
        doAjaxResponseForm(responseJSON, e);
    });
});
