const DARKREADER_CONFIG = {
    contrast: 120
};
DarkReader.setFetchMethod(window.fetch); // solves CORS issue

var onDarkModeChange = function() {};

function enableDarkMode(isVoluntary) {
    DarkReader.enable(DARKREADER_CONFIG);

    const elemDarkModeSwitch = $("#dark-mode-switch");
    if (!elemDarkModeSwitch.prop("checked")) {
        elemDarkModeSwitch.prop("checked", true);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "true");
    }

    onDarkModeChange();
}

function disableDarkMode(isVoluntary) {
    DarkReader.disable();

    const elemDarkModeSwitch = $("#dark-mode-switch");
    if (elemDarkModeSwitch.prop("checked")) {
        elemDarkModeSwitch.prop("checked", false);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "false");
    }

    onDarkModeChange();
}

$(document).ready(function() {
    const elemDarkModeSwitch = $("#dark-mode-switch");

    // if set to dark mode on JS load (below), make sure to sync switch state once the switch loads in
    if (DarkReader.isEnabled()) {
        elemDarkModeSwitch.prop("checked", true);
    } else {
        elemDarkModeSwitch.prop("checked", false);
    }

    // if defaulting to system setting, detect change in system setting
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
        if (localStorage.getItem("darkMode") === null) {
            var newColorScheme = e.matches ? "dark" : "light";
            if (e.matches) {
                enableDarkMode(false);
            } else {
                disableDarkMode(false);
            }
        }
    });

    // not triggered by prop(); detects manual change in switch state and activates/deactivates DarkReader
    elemDarkModeSwitch.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode(true);
        } else {
            disableDarkMode(true);
        }
    });
});

/* Out here so it's immediately applied on JS load instead of at `$(document).ready` */
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode(false);
} else if (localStorage.getItem("darkMode") === null
        && window.matchMedia
        && window.matchMedia("(prefers-color-scheme: dark)").matches) { // default to system setting
    enableDarkMode(false);
}
