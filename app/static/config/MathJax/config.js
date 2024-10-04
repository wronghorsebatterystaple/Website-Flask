let onMathJaxTypeset = function(baseSelector) {
    const jQBase = $(baseSelector);
    if (!jQBase) {
        return;
    }

    // make \[\] LaTeX blocks scroll horizontally on overflow
    jQBase.find("mjx-math[style='margin-left: 0px; margin-right: 0px;']").wrap(HORIZ_SCOLL_DIV_HTML);
    jQBase.find("mjx-math[width='full']").each(function() {
        $(this).parent("mjx-container").css("min-width", ""); // can cause overflow problems
        $(this).wrap(HORIZ_SCOLL_DIV_HTML_WIDTH_FULL);        // for \tag{}ed
    });
}

window.MathJax = {
    tex: {
        /**
         * Custom commands from my file server sync.
         *
         * Missing:
         *    - `\exists`       (= `\exists\,`)
         *    - `\existsunique` (= `\exists!\,`)
         *    - `\forall`       (= `\forall\c`)
         */
        macros: {
            // redefined functions to always use parentheses around arguments
            Arccos: [`\arccos{\left(#1\right)}`, 1],
            Arccot: [`\arccot{\left(#1\right)}`, 1],
            Arccsc: [`\arccsc{\left(#1\right)}`, 1],
            Arcsec: [`\arcsec{\left(#1\right)}`, 1],
            Arcsin: [`\arcsin{\left(#1\right)}`, 1],
            Arctan: [`\arctan{\left(#1\right)}`, 1],
            Cos: [`\cos{\left(#1\right)}`, 1],
            Cot: [`\cot{\left(#1\right)}`, 1],
            Csc: [`\csc{\left(#1\right)}`, 1],
            Int: [`\int_{#1}^{#2}{\left(#3\right)}`, 3],
            Lim: [`\lim_{#1}{\left(#2\right)}`, 2],
            Log: [`\log_{#1}{\left(#2\right)}`, 2],
            Ln: [`\ln{\left(#1\right)}`, 1],
            Sec: [`\sec{\left(#1\right)}`, 1],
            Sin: [`\sin{\left(#1\right)}`, 1],
            Sum: [`\sum_{#1}^{#2}{\left(#3\right)}`, 3],
            Tan: [`\tan{\left(#1\right)}`, 1],

            // other commands
            andd: `\text{ and }`,
            b: [`\textcolor{blue}{#1}`, 1],
            C: `\mathbb{C}`,
            c: `,\,`,
            cand: `,\, \text{and }`,
            ceil: [`\left\lceil #1 \right\rceil`, 1],
            choose: [`\begin{pmatrix} #1 \\ #2 \end{pmatrix}`, 2],
            comb: [`{}^{#1}C_{#2}`, 2],
            cor: `,\, \text{or }`,
            ddx: [`\frac{\mathrm{d}}{\mathrm{d} #1}`, 1],
            divs: `\mid`,
            DNE: `\text{DNE}`,
            domain: `\text{domain}`,
            dx: [`\,\mathrm{d} #1`, 1],
            dydx: [`\frac{\mathrm{d} #1}{\mathrm{d} #2}`, 2],
            F: `\mathbb{F}`,
            floor: [`\left\lfloor #1 \right\rfloor`, 1],
            ftc: [`\left[#3\right]_{#1}^{#2}`, 3],
            gcd: `\text{gcd}`,
            given: `\,\vert\,`,
            givenlr: `\,\middle\vert\,`,
            iffshort: `\Leftrightarrow`,
            impliesshort: `\Rightarrow`,
            lcm: `\text{lcm}`,
            mod: `\text{ mod }`,
            multichoose: [`\left(\!\!\choose{#1}{#2}\!\!\right)`, 2],
            N: `\mathbb{N}`,
            nequiv: `\not\equiv`,
            notdivs: `\nmid`,
            orr: `\text{ or }`,
            p: [`\phantom{#1}`, 1],
            Perm: `\text{Perm}`,
            perm: [`{}^{#1}P_{#2}`, 2],
            pfpxpy: [`\frac{\partial^2 #1}{\partial #2 \partial #3}`, 3],
            powerset: `\mathcal{P}`,
            ppx: [`\frac{\partial}{\partial #1}`, 1],
            ppxpy: [`\frac{\partial^2}{\partial #1 \partial #2}`, 2],
            pypx: [`\frac{\partial #1}{\partial #2}`, 2],
            Q: `\mathbb{Q}`,
            R: `\mathbb{R}`,
            r: [`\textcolor{red}{#1}`, 1],
            range: `\text{range}}`,
            st: `\text{ s.t. }`,
            suchthat: `\,\vert\,`,
            suchthatlr: `\,\middle\vert\,`,
            Sym: `\text{Sym}`,
            Var: `\text{Var}`,
            t: `\text`,
            Z: `\mathbb{Z}`
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
