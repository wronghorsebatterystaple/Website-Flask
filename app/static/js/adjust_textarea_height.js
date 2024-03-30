function adjustTextareaHeight(textarea_dom) {
    textarea_dom.style.height = "";
    textarea_dom.style.height = textarea_dom.scrollHeight + 3 + "px";
}

window.addEventListener("load", function() {
    $("textarea").each(function() {
        adjustTextareaHeight($(this).get(0));
    });
});

$(document).on("input", "textarea", function(e) {
    adjustTextareaHeight(e.target);
});
