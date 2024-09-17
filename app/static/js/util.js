const HORIZ_SCOLL_DIV_HTML = "<div class=\"scroll-overflow-x\"></div>";
const HORIZ_SCOLL_DIV_HTML_WIDTH_FULL = "<div class=\"scroll-overflow-x\" width=\"full\"></div>";

/**
 * Preconditions:
 *     - Only use on functions that have already been initialized! Remember that hoisting does not hoist
 *       initializations; thus, JS files containing these functions must not be deferred and must be linked first!
 *
 * Usage:
 *     ```
 *     func1 = addToFunction(func1, func2);
 *     ```
 */
function addToFunction(functionBase, functionToAdd) {
    return function() {
        functionBase.apply(this, arguments);
        functionToAdd.apply(this, arguments);
    };
}

function getCurrUrlNoParams(includeScheme=true) {
    if (includeScheme) {
        return window.location.origin + window.location.pathname;
    } else {
        return window.location.host + window.location.pathname;
    }
}
