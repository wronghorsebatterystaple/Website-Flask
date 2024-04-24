function onAdminFormAjaxDone(response, e) {
    processStandardAjaxResponse(response, e);
}

$(document).on("submit", "form", function(e) {
    e.preventDefault();
  
    var formData = new FormData($(this).get(0), $(e.originalEvent.submitter).get(0));
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
        handleCustomErrors(jqXHR, formData, e, self, onAdminFormAjaxDone);
    });
});
