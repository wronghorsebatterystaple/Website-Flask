onDarkModeChange = addToFunction(onDarkModeChange, function(enabled) {
    const jQFooterIconGitHub = $("#footer__github-icon");
    if (!jQFooterIconGitHub) {
        return;
    }

    if (enabled) {
        jQFooterIconGitHub.attr("src", URL_ICON_GITHUB_DARK);
    } else {
        jQFooterIconGitHub.attr("src", URL_ICON_GITHUB_LIGHT);
    }
});
