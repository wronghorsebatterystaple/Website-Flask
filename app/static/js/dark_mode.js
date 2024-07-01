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

    if (DarkReader.isEnabled()) { // make sure switch state is correct; wait for $(document).ready so the element is loaded
        darkModeSwitch_elem.prop("checked", true);
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
} else if (localStorage.getItem("darkMode") === null) { // default to system settings; don't set localStorage
    DarkReader.auto(DARKREADER_CONFIG);
}
