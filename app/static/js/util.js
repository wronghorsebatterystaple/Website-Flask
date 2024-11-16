const HORIZ_SCOLL_DIV_HTML = '<div class="scroll-overflow-x"></div>';
const HORIZ_SCOLL_DIV_HTML_FULL_WIDTH = '<div class="scroll-overflow-x" width="full"></div>';

/**
 * Preconditions:
 *     - Target function(s) must have already been initialized
 *
 * Usage:
 *     ```
 *     func1 = addToFunction(func1, func2);
 *     ```
 *     - Make sure the two funcs have the same params
 */
function addToFunction(functionBase, functionToAdd) {
    return function() {
        functionBase.apply(this, arguments);
        functionToAdd.apply(this, arguments);
    };
}
