const DARKREADER_CONFIG = {
    constrast: 120
};
DarkReader.setFetchMethod(window.fetch); // solves CORS issue

function enableDarkMode(isManual) {
    if (isManual) {
        localStorage.setItem("darkMode", "true");
    }
    DarkReader.enable(DARKREADER_CONFIG);
}

function disableDarkMode(isManual) {
    if (isManual) {
        localStorage.setItem("darkMode", "false");
    }
    DarkReader.disable();
}

$(document).ready(function() {
    const darkModeSwitch_elem = $("#dark-mode-switch");

    // if set to dark mode on JS load (below), make sure to sync switch state once the switch loads in
    if (DarkReader.isEnabled()) {
        darkModeSwitch_elem.prop("checked", true);
    } else { // if you delete the localStorage item and refresh, it can be light mode but switch checked
        darkModeSwitch_elem.prop("checked", false);
    }

    // default to system settings; control using switch state
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
        if (localStorage.getItem("darkMode") === null) {
            var newColorScheme = e.matches ? "dark" : "light";
            if (e.matches) {
                darkModeSwitch_elem.prop("checked", true);
                enableDarkMode(false);
            } else {
                darkModeSwitch_elem.prop("checked", false);
                disableDarkMode(false);
            }
        }
    });

    // not triggered by prop(); detects manual change in switch state and activates/deactivates DarkReader
    darkModeSwitch_elem.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode(true);
        } else {
            disableDarkMode(true);
        }
    });
});

// Out here so it's immediately applied on JS load instead of at $(document).ready
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode(false);
} else if (localStorage.getItem("darkMode") === null && window.matchMedia
        && window.matchMedia("(prefers-color-scheme: dark)").matches) { // if defaulting to system setting
    enableDarkMode(false);
}
