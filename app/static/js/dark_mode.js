function enableDarkMode() {
     DarkReader.setFetchMethod(window.fetch); // solves CORS issue
     DarkReader.enable();
}

function disableDarkMode() {
    DarkReader.disable();
}

$(document).ready(function() {
    const darkModeSwitch_elem = $("#dark-mode-switch");

    darkModeSwitch_elem.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode();
            localStorage.setItem("darkMode", "true");
        } else {
            disableDarkMode();
            localStorage.setItem("darkMode", "false");
        }
    });

    if (localStorage.getItem("darkMode") === "true") {
        darkModeSwitch_elem.prop("checked", true);
    }
});

if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode();
}
