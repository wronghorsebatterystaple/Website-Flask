const HORIZ_SCOLL_DIV_HTML = "<div class=\"scroll-overflow-x\"></div>";
const HORIZ_SCOLL_DIV_HTML_WIDTH_FULL = "<div class=\"scroll-overflow-x\" width=\"full\"></div>";

/**
 * Preconditions:
 *     - Only use on functions that have already been initialized! Remember that hoisting does not hoist
 *       initializations; thus, JS files containing these function initializations must be executed before
 *       attempting to invoke `addToFunction()` on them!
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
