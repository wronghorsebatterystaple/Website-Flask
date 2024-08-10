/**
 * Usage: `func1 = addToFunction(func1, func2);`
 */
function addToFunction(functionBase, functionToAdd) {
    functionBase = function() {
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
