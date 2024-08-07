/**
 * Usage: `func = addToFunction(func, func2);`
 */
function addToFunction(functionBase, functionToAdd) {
    return function() {
        functionBase.apply(this, arguments);
        functionToAdd.apply(this, arguments);
    };
}

function getCurrentURLNoQS(includeScheme=true) {
    if (includeScheme) {
        return window.location.origin + window.location.pathname;
    } else {
        return window.location.host + window.location.pathname;
    }
}
