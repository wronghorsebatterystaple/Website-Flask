randomizeColors();

// it seems like this doesn't *have* to be before dark mode, but putting it before just because it makes sense
function randomizeColors() {
    const colorChoicesSelection = ["--custom-blue-xxlight", "--custom-green-deep-xlight", "--custom-pink-xxlight"];
    let rand = Math.floor(Math.random() * colorChoicesSelection.length);
    $(document).append(`
        <style>
            ::selection {
                background-color: var(${colorChoicesSelection[rand]}) !important;
            }
        </style>
    `);

    const colorChoicesFlash = [
        ["--custom-blue-light", "--custom-blue-xxxlight"],
        ["--custom-green", "--custom-green-xxxlight"],
        ["--custom-orange-light", "--custom-orange-xxxlight"],
        ["--custom-pink-xlight", "--custom-pink-xxxlight"]
    ];
    rand = Math.floor(Math.random() * colorChoicesFlash.length);
    $("#flash")
            .css("border-color", `var(${colorChoicesFlash[rand][0]}) !important`)
            .css("background-color", `var(${colorChoicesFlash[rand][1]}) !important`);
}
