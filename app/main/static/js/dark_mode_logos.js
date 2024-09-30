onDarkModeChange = addToFunction(onDarkModeChange, function(enabled) {
    const jQFooterIconGitHub = $("#footer__github-icon");
    if (!jQFooterIconGitHub) {
        return;
    }

    if (enabled) {
        jQFooterIconGitHub.attr("src", ICON_GITHUB_DARK_URL);
    } else {
        jQFooterIconGitHub.attr("src", ICON_GITHUB_LIGHT_URL);
    }
});
