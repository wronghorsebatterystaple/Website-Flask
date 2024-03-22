$(".reply-btn").submit(function(e) {
    e.preventDefault();

    var id = $(this).attr("id").match(/\d+/)[0] // get matching id number
    $(`#reply-form-${id}`).removeAttr("hidden");
    $(`#reply-form-${id}`).find("#parent").attr("value", id); // insert under right parent
});
