const DARKREADER_OPTIONS = {
    contrast: 130
};
const DARKREADER_FIXES = {
    // CSS selectors for elements that are not automatically inverted by DarkReader (images, SVG icons etc.)
    invert: [
        ".dark-mode-manual"
    ]
}

DarkReader.setFetchMethod(window.fetch); // solves CORS issue

let onDarkModeChange = function(enabled) {};

// out here so it's immediately applied on JS load instead of at `$(document).ready()`
let jQSwitchDarkMode = null;
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode(false);
} else if (localStorage.getItem("darkMode") === null
        && window.matchMedia
        && window.matchMedia("(prefers-color-scheme: dark)").matches) { // default to system setting
    enableDarkMode(false);
}

function enableDarkMode(isVoluntary) {
    DarkReader.enable(DARKREADER_OPTIONS, DARKREADER_FIXES);

    if (jQSwitchDarkMode && !jQSwitchDarkMode.prop("checked")) {
        jQSwitchDarkMode.prop("checked", true);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "true");
    }

    // only call after `$(document).ready()` in case we need to modify DOM elements
    if (jQuery.isReady) {
        onDarkModeChange(true);
    }
}

function disableDarkMode(isVoluntary) {
    DarkReader.disable();

    if (jQSwitchDarkMode && jQSwitchDarkMode.prop("checked")) {
        jQSwitchDarkMode.prop("checked", false);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "false");
    }

    if (jQuery.isReady) {
        onDarkModeChange(false);
    }
}

$(document).ready(function() {
    jQSwitchDarkMode = $("#switch--dark-mode");

    // if set to dark mode on JS load, make sure to sync switch state once the switch loads in
    // also make sure `onDarkModeChange()` is called once everything is loaded
    if (DarkReader.isEnabled()) {
        jQSwitchDarkMode.prop("checked", true);
        onDarkModeChange(true);
    } else {
        jQSwitchDarkMode.prop("checked", false);
        onDarkModeChange(false);
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
    jQSwitchDarkMode.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode(true);
        } else {
            disableDarkMode(true);
        }
    });
});
