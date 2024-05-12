function togglePasswordVisibility(inputId, showId) {
    var input_elem = $(`#${inputId}`);
    if (input_elem.attr("type") == "password") {
        input_elem.attr("type", "text");
    } else {
        input_elem.attr("type", "password");
    }

    $(`#${showId}`).get(0).classList.toggle("bi-eye");
}
