$(document).ready(function() {
    $("#main-form").on("submit", async function(e) {
        e.preventDefault();
      
        const jQSubmitter = $(e.originalEvent.submitter);
        let formData = new FormData(e.target);
        const respJson = await fetchWrapper(window.location.href, {method: "POST", body: formData});
        doAjaxResponseForm(respJson, e);
    });
});
