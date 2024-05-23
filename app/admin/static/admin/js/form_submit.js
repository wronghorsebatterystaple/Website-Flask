function onAdminFormAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);
}

$(document).ready(function() {
    $("#main-form").on("submit", function(e) {
        e.preventDefault();
      
        if (e.originalEvent.submitter.id === "cancel-images-btn") {
            $("#images-input").val("");
            return;
        }

        var formData = new FormData(e.target, e.originalEvent.submitter);
        $.ajax({
            type: "POST",
            url: window.location.pathname + window.location.search,
            data: formData,
            processData: false,
            contentType: false,
            dataType: "json"
        })
        .done(function(response) {
            onAdminFormAjaxDone(response, e);
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            var self = this;
            handleAjaxErrors(jqXHR, formData, e, self, onAdminFormAjaxDone);
        });
    });
});
