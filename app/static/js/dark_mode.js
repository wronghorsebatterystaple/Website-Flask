const DARKREADER_CONFIG = {
    constrast: 120
};
DarkReader.setFetchMethod(window.fetch); // solves CORS issue

function enableDarkMode() {
     localStorage.setItem("darkMode", "true");
     DarkReader.enable(DARKREADER_CONFIG);
}

function disableDarkMode() {
    localStorage.setItem("darkMode", "false");
    DarkReader.disable();
}

$(document).ready(function() {
    const darkModeSwitch_elem = $("#dark-mode-switch");

    if (localStorage.getItem("darkMode") === "true") {      // make sure switch state is correct
        darkModeSwitch_elem.prop("checked", true);
    } else if (localStorage.getItem("darkMode") === null) { // default to system settings; don't set localStorage
        DarkReader.auto(DARKREADER_CONFIG);
        if (DarkReader.isEnabled()) {                       // also make sure switch state is correct here
            darkModeSwitch_elem.prop("checked", true);
        }
    }

    darkModeSwitch_elem.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
    });
});

// Out here so it's immediately applied on JS load instead of at $(document).ready
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode();
}
