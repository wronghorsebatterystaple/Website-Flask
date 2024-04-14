function adjustTextareaHeight(textarea_dom) {
    if (textarea_dom.style.height != textarea_dom.scrollHeight) {
        textarea_dom.style.height = "";
        textarea_dom.style.height = `${textarea_dom.scrollHeight + 1.5}px`;
    }
}

$(document).ready(function() {
    $("textarea").each(function() {
        adjustTextareaHeight($(this).get(0));
    });
});

$(document).on("input", "textarea", function(e) {
    adjustTextareaHeight(e.target);
});
