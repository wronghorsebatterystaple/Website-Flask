const DARKREADER_CONFIG = {
    contrast: 120
};
DarkReader.setFetchMethod(window.fetch); // solves CORS issue

// out here so it's immediately applied on JS load instead of at `$(document).ready`
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode(false);
} else if (localStorage.getItem("darkMode") === null
        && window.matchMedia
        && window.matchMedia("(prefers-color-scheme: dark)").matches) { // default to system setting
    enableDarkMode(false);
}

function enableDarkMode(isVoluntary) {
    DarkReader.enable(DARKREADER_CONFIG);

    const jQueryDarkModeSwitch = $("#dark-mode-switch");
    if (!jQueryDarkModeSwitch.prop("checked")) {
        jQueryDarkModeSwitch.prop("checked", true);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "true");
    }
}

function disableDarkMode(isVoluntary) {
    DarkReader.disable();

    const jQueryDarkModeSwitch = $("#dark-mode-switch");
    if (jQueryDarkModeSwitch.prop("checked")) {
        jQueryDarkModeSwitch.prop("checked", false);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "false");
    }
}

$(document).ready(function() {
    const jQueryDarkModeSwitch = $("#dark-mode-switch");

    // if set to dark mode on JS load (below), make sure to sync switch state once the switch loads in
    if (DarkReader.isEnabled()) {
        jQueryDarkModeSwitch.prop("checked", true);
    } else {
        jQueryDarkModeSwitch.prop("checked", false);
    }

    // if defaulting to system setting, detect change in system setting
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function(e) {
        if (localStorage.getItem("darkMode") === null) {
            let newColorScheme = e.matches ? "dark" : "light";
            if (e.matches) {
                enableDarkMode(false);
            } else {
                disableDarkMode(false);
            }
        }
    });

    // not triggered by prop(); detects manual change in switch state and activates/deactivates DarkReader
    jQueryDarkModeSwitch.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode(true);
        } else {
            disableDarkMode(true);
        }
    });
});
