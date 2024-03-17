var flash_id = 0;

function custom_flash(message) {
    var new_message = $("#flash-message-template").clone();
    var new_message_text = new_message.children("#flash-message-template-text");
    new_message.attr("id", `flash-message-${flash_id}`);
    new_message_text.attr("id", `flash-message-${flash_id}-text`);
    flash_id++;
    new_message_text.text(message);
    new_message.appendTo("#flash-container");
    new_message.removeAttr("hidden");
}

