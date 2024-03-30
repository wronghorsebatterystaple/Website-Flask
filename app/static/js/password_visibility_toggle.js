function togglePasswordVisibility(inputID, showID) {
    var input_elem = $(`#${inputID}`);
    if (input_elem.attr("type") == "password") {
        input_elem.attr("type", "text");
    } else {
        input_elem.attr("type", "password");
    }

    $(`#${showID}`).get(0).classList.toggle("bi-eye");
}
