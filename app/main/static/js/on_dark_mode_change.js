onDarkModeChange = addToFunction(onDarkModeChange, function(enabled) {
    if (enabled) {
        $("#footer__icon--github").attr("src", URL_ICON_GITHUB_DARK);
    } else {
        $("#footer__icon--github").attr("src", URL_ICON_GITHUB_LIGHT);
    }
});
