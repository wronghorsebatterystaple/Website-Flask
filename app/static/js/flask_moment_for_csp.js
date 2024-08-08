moment.locale("en");

function flask_moment_render(elem) {{
    const timestamp = moment(elem.dataset.timestamp);
    const func = elem.dataset.function;
    const format = elem.dataset.format;
    const timestamp2 = elem.dataset.timestamp2;
    const no_suffix = elem.dataset.nosuffix;
    const units = elem.dataset.units;
    let args = [];

    if (format) {
        args.push(format);
    }
    if (timestamp2) {
        args.push(moment(timestamp2));
    }
    if (no_suffix) {
        args.push(no_suffix);
    }
    if (units) {
        args.push(units);
    }

    elem.textContent = timestamp[func].apply(timestamp, args);
    elem.classList.remove("flask-moment");
    elem.style.display = "";
}}

function flask_moment_render_all() {{
    const moments = document.querySelectorAll(".flask-moment");
    moments.forEach(function(moment) {{
        flask_moment_render(moment);
        const refresh = moment.dataset.refresh;
        if (refresh && refresh > 0) {{
            (function(elem, interval) {{
                setInterval(function() {{
                    flask_moment_render(elem);
                }}, interval);
            }})(moment, refresh);
        }}
    }})
}}

$(document).ready(flask_moment_render_all);
