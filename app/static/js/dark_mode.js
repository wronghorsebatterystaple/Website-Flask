const DARKREADER_OPTIONS = {
    contrast: 120
};
const DARKREADER_FIXES = {
    // CSS selectors for elements that are not automatically inverted by DarkReader (images, SVG icons etc.)
    invert: [
        ".darkreader-manual",
        ".post__img"
    ]
}

DarkReader.setFetchMethod(window.fetch); // solves CORS issue

// out here so it's immediately applied on JS load instead of at `$(document).ready`
let jQuerySwitchDarkMode = null;
if (localStorage.getItem("darkMode") === "true") {
    enableDarkMode(false);
} else if (localStorage.getItem("darkMode") === null
        && window.matchMedia
        && window.matchMedia("(prefers-color-scheme: dark)").matches) { // default to system setting
    enableDarkMode(false);
}

function enableDarkMode(isVoluntary) {
    DarkReader.enable(DARKREADER_OPTIONS, DARKREADER_FIXES);

    if (jQuerySwitchDarkMode && !jQuerySwitchDarkMode.prop("checked")) {
        jQuerySwitchDarkMode.prop("checked", true);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "true");
    }
}

function disableDarkMode(isVoluntary) {
    DarkReader.disable();

    if (jQuerySwitchDarkMode && jQuerySwitchDarkMode.prop("checked")) {
        jQuerySwitchDarkMode.prop("checked", false);
    }

    if (isVoluntary) {
        localStorage.setItem("darkMode", "false");
    }
}

$(document).ready(function() {
    jQuerySwitchDarkMode = $("#switch--dark-mode");

    // if set to dark mode on JS load (below), make sure to sync switch state once the switch loads in
    if (DarkReader.isEnabled()) {
        jQuerySwitchDarkMode.prop("checked", true);
    } else {
        jQuerySwitchDarkMode.prop("checked", false);
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
    jQuerySwitchDarkMode.on("change", function(e) {
        if (e.target.checked) {
            enableDarkMode(true);
        } else {
            disableDarkMode(true);
        }
    });
});
