$(document).ready(function() {
    $("#main-form").on("submit", async function(e) {
        e.preventDefault();
      
        const jQuerySubmitter = $(e.originalEvent.submitter);
        if (jQuerySubmitter.is("[data-no-submit]")) {
            switch (jQuerySubmitter.attr("id")) {
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
        const respJson = await fetchWrapper(window.location.href, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);
    });
});
