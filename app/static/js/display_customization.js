$(document).ready(function() {
    $("mjx-math[style='margin-left: 0px; margin-right: 0px;']").addClass("mjx-center");
    $(".mjx-center").css("font-size", "clamp(85%, 3.25vw, 100%)");

    $("table").find("p").addClass("mb-0"); // markdown_grid_tables tables generate <p> tags with too much spacing
    $("table").each(function() {
        if ($(this).find("pre").length > 0) {
            $(this).addClass("fixed-table-layout"); // tables containing code blocks have equal width cols (scuffed)
        }
    });
    $("td").each(function() {
        if ($(this).find("pre").length > 0) {
            $(this).addClass("align-top"); // cells containing code blocks are top-aligned
            $(this).find("pre").addClass("mb-0");
        }
    });
});
