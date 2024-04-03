window.MathJax = {
    tex: {
        macros: {
            // simple math symbols
            divs: "\\mid",
            F: "\\textbf{F}",
            given: "\\,\\vert\\,",
            givenlong: "\\,\\middle\\vert\\,",
            nequiv: "\\not\\equiv",
            notdivs: "\\nmid",
            powerset: "\\mathcal{P}",
            suchthat: "\\,\\vert\\,",
            suchthatlong: "\\,\\middle\\vert\\,",
            // redifined functions to always use parenthesess around arguments
            Arccos: ["\\arccos{\\left(#1\\right)}", 1],
            Arccot: ["\\arccot{\\left(#1\\right)}", 1],
            Arccsc: ["\\arccsc{\\left(#1\\right)}", 1],
            Arcsec: ["\\arcsec{\\left(#1\\right)}", 1],
            Arcsin: ["\\arcsin{\\left(#1\\right)}", 1],
            Arctan: ["\\arctan{\\left(#1\\right)}", 1],
            Cos: ["\\cos{\\left(#1\\right)}", 1],
            Cot: ["\\cot{\\left(#1\\right)}", 1],
            Csc: ["\\csc{\\left(#1\\right)}", 1],
            Int: ["\\int_{#1}^{#2}{\\left(#3\\right)}", 3],
            Lim: ["\\lim_{#1}{\\left(#2\\right)}", 2],
            Log: ["\\log_{#1}{\\left(#2\\right)}", 2],
            Ln: ["\\ln{\\left(#1\\right)}", 1],
            Sec: ["\\sec{\\left(#1\\right)}", 1],
            Sin: ["\\sin{\\left(#1\\right)}", 1],
            Sum: ["\\sum_{#1}^{#2}{\\left(#3\\right)}", 3],
            Tan: ["\\tan{\\left(#1\\right)}", 1],
            // other math notations and shorthands
            ceil: ["\\left\\lceil #1 \\right\\rceil", 1],
            choose: ["\\begin{pmatrix} #1 \\\\ #2 \\end{pmatrix}", 2],
            comb: ["^{#1}C_{#2}", 2],
            ddx: ["\\frac{\\mathrm{d}}{\\mathrm{d} #1}", 1],
            dydx: ["\\frac{\\mathrm{d} #1}{\\mathrm{d} #2}", 2],
            dx: ["\\,\\mathrm{d} #1", 1],
            floor: ["\\left\\lfloor #1 \\right\\rfloor", 1],
            ftc: ["\\left[#3\\right]_{#1}^{#2}", 3],
            multichoose: ["\\left(\\!\\!\\choose{#1}{#2}\\!\\!\\right)", 2],
            perm: ["^{#1}P_{#2}", 2],
            ppx: ["\\frac{\\partial}{\\partial #1}", 1],
            pypx: ["\\frac{\\partial #1}{\\partial #2}", 2],
            // text
            andd: "\\text{ and }",
            cand: ",\\, \\text{and }",
            c: ",\\,",
            cor: ",\\, \\text{or }",
            DNE: "\\text{DNE}",
            gcd: "\\text{gcd}",
            lcm: "\\text{lcm}",
            mod: "\\text{ mod }",
            orr: "\\text{ or }",
            st: "\\text{ s.t. }",
            t: "\\text"
        }
    }
};
