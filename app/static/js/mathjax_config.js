let onMathJaxTypeset = function(baseSelector) {
    const jQBase = $(baseSelector);
    if (!jQBase) {
        return;
    }

    // make \[\] LaTeX blocks scroll horizontally on overflow
    jQBase.find("mjx-math[style='margin-left: 0px; margin-right: 0px;']").wrap(HORIZ_SCOLL_DIV_HTML);
    // for `\tag{}`ed equations
    jQBase.find("mjx-math[width='full']").each(function() {
        $(this).parent("mjx-container").css("min-width", ""); // otherwise text just overflows
        $(this).wrap(HORIZ_SCOLL_DIV_HTML_FULL_WIDTH);
    });
}

window.MathJax = {
    tex: {
        // custom commands from my notes (or all the ones MathJax supports, at least)
        macros: {
            arccot: "\\operatorname{arccot}",
            arccsc: "\\operatorname{arccsc}",
            arcsec: "\\operatorname{arcsec}",
            Aut: "\\operatorname{Aut}",
            C: "\\mathbb{C}",
            ceil: ["\\left\\lceil #1 \\right\\rceil", 1],
            choose: ["\\begin{pmatrix} #1 \\\\ #2 \\end{pmatrix}", 2],
            codom: ["\\operatorname{codom}"],
            coloneq: ["\\mathrel{≔}"],
            comb: ["{}^{#1}C_{#2}", 2],
            ddx: ["\\frac{\\mathrm{d}}{\\mathrm{d} #1}", 1],
            dist: "\\operatorname{dist}",
            dom: "\\operatorname{dom}",
            dx: ["\\,\\mathrm{d} #1", 1],
            dydx: ["\\frac{\\mathrm{d} #1}{\\mathrm{d} #2}", 2],
            F: "\\mathbb{F}",
            Fix: "\\operatorname{Fix}",
            floor: ["\\left\\lfloor #1 \\right\\rfloor", 1],
            ftc: ["\\left[#3\\right]_{#1}^{#2}", 3],
            generator: ["\\langle #1 \\rangle", 1],
            id: "\\operatorname{id}",
            iffshort: "\\Leftrightarrow",
            im: "\\operatorname{id}",
            impliesshort: "\\Rightarrow",
            innprod: ["\\langle #1 \\rangle", 1],
            lcm: "\\operatorname{lcm}",
            multichoose: ["\\left(\\!\\!\\choose{#1}{#2}\\!\\!\\right)", 2],
            N: "\\mathbb{N}",
            nequiv: "\\not\\equiv",
            niff: "\\centernot\\iff",
            niffshort: "\\nLeftrightarrow",
            nimplies: "\\centernot\\implies",
            nimpliesshort: "\\nRightarrow",
            nul: "\\operatorname{nul}",
            Orb: "\\operatorname{Orb}",
            Perm: "\\operatorname{Perm}",
            perm: ["{}^{#1}P_{#2}", 2],
            pfpxpy: ["\\frac{\\partial^2 #1}{\\partial #2 \\partial #3}", 3],
            powerset: "\\mathcal{P}",
            ppx: ["\\frac{\\partial}{\\partial #1}", 1],
            ppxpy: ["\\frac{\\partial^2}{\\partial #1 \\partial #2}", 2],
            preim: "\\operatorname{preim}",
            pypx: ["\\frac{\\partial #1}{\\partial #2}", 2],
            Q: "\\mathbb{Q}",
            R: "\\mathbb{R}",
            range: "\\operatorname{range}",
            rank: "\\operatorname{rank}",
            sgn: "\\operatorname{sgn}",
            spann: "\\operatorname{span}",
            Stab: "\\operatorname{Stab}",
            suchthat: "\\,\\vert\\,",
            suchthatlr: "\\,\\middle\\vert\\,",
            Sum: ["\\sum_{#1}^{#2}{\\left(#3\\right)}", 3],
            Sym: "\\operatorname{Sym}",
            tobij: "\\leftrightarrow",
            toinc: "\\hookrightarrow",
            toinj: "\\rightarrowtail",
            toiso: "\\xrightarrow{\\sim}",
            tosur: "\\twoheadrightarrow",
            Z: "\\mathbb{Z}"
        }
    },
    startup: {
        ready: function() {
            MathJax.startup.defaultReady();
            MathJax.startup.promise.then(function() {
                onMathJaxTypeset("body");
            });
        }
    }
};
