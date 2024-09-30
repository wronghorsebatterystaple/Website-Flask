let rand = Math.floor(Math.random() * 3);
backgroundImgName = `background_${rand}.png`;

$(document).ready(function() {
    // don't show white background on navbar (originally for sticky) for this custom colorful background
    document.getElementById("navbar").classList.remove("bg-white");
});
