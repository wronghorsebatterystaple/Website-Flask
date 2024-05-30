function enableDarkMode() {
     DarkReader.setFetchMethod(window.fetch); // solves CORS issue
     DarkReader.enable();
}

function disableDarkMode() {
    DarkReader.disable();
}

$(document).ready(function() {
    $("#dark-mode-switch").on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
    });
});
