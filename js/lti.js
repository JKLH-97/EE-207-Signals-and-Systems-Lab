/* =========================================================
   EE-207 SIGNALS & SYSTEMS
   Chapter 01 — LTI Systems
   ========================================================= */

const LTI = (() => {

    /* -----------------------------------------------------
       INTERNAL STATE
    ----------------------------------------------------- */

    const state = {
        activeTab: "concept"
    };


    /* -----------------------------------------------------
       TAB DEFINITIONS
    ----------------------------------------------------- */

    const tabs = [
        { id: "concept", label: "Concept" },
        { id: "linearity", label: "Linearity Lab" },
        { id: "time-invariance", label: "Time-Invariance Lab" },
        { id: "lti-lab", label: "LTI Lab" },
        { id: "system-grapher", label: "System Grapher" },
        { id: "mini-exam", label: "Mini Exam" }
    ];


    /* -----------------------------------------------------
       MAIN RENDER
    ----------------------------------------------------- */

    function render() {

        const container = document.getElementById("lti");

        if (!container) return;

        container.innerHTML = `
            <div class="chapter-shell">

                <header class="chapter-header">

                    <div class="chapter-title-block">
                        <span class="chapter-number">
                            CHAPTER 01
                        </span>

                        <h1>LTI Systems</h1>

                        <p>
                            Explore linearity and time invariance
                            graphically and interactively.
                        </p>
                    </div>

                </header>


                <nav
                    class="chapter-tabs"
                    aria-label="LTI Systems sections"
                >
                    ${tabs.map(tab => `
                        <button
                            class="chapter-tab
                            ${tab.id === state.activeTab ? "active" : ""}"
                            data-lti-tab="${tab.id}"
                        >
                            ${tab.label}
                        </button>
                    `).join("")}
                </nav>


                <div
                    class="chapter-content"
                    id="lti-content"
                ></div>

            </div>
        `;

        bindTabs();

        renderActiveTab();
    }


    /* -----------------------------------------------------
       TAB NAVIGATION
    ----------------------------------------------------- */

    function bindTabs() {

        const buttons =
            document.querySelectorAll(
                "[data-lti-tab]"
            );

        buttons.forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    state.activeTab =
                        button.dataset.ltiTab;

                    updateTabStyles();

                    renderActiveTab();
                }
            );

        });
    }


    function updateTabStyles() {

        document
            .querySelectorAll("[data-lti-tab]")
            .forEach(button => {

                button.classList.toggle(
                    "active",
                    button.dataset.ltiTab ===
                    state.activeTab
                );

            });
    }


    /* -----------------------------------------------------
       ACTIVE TAB ROUTER
    ----------------------------------------------------- */

    function renderActiveTab() {

        const content =
            document.getElementById(
                "lti-content"
            );

        if (!content) return;


        switch (state.activeTab) {

            case "concept":
                renderConcept(content);
                break;

            case "linearity":
                renderPlaceholder(
                    content,
                    "Linearity Lab"
                );
                break;

            case "time-invariance":
                renderPlaceholder(
                    content,
                    "Time-Invariance Lab"
                );
                break;

            case "lti-lab":
                renderPlaceholder(
                    content,
                    "LTI Lab"
                );
                break;

            case "system-grapher":
                renderPlaceholder(
                    content,
                    "System Grapher"
                );
                break;

            case "mini-exam":
                renderPlaceholder(
                    content,
                    "Mini Exam"
                );
                break;
        }
    }


    /* -----------------------------------------------------
       CONCEPT
    ----------------------------------------------------- */

    function renderConcept(container) {

        container.innerHTML = `

            <section class="lti-concept">

                <h2>
                    What makes a system LTI?
                </h2>


                <div class="concept-grid">

                    <!-- LINEARITY -->
                    <article class="concept-panel">

                        <span class="concept-index">
                            1
                        </span>

                        <h3>Linearity</h3>

                        <div class="equation-box">
                            T{a x₁(t) + b x₂(t)}
                            =
                            aT{x₁(t)} + bT{x₂(t)}
                        </div>

                        <p>
                            The order of combining or scaling
                            signals and applying the system
                            must not matter.
                        </p>

                    </article>


                    <!-- TIME INVARIANCE -->
                    <article class="concept-panel">

                        <span class="concept-index">
                            2
                        </span>

                        <h3>Time Invariance</h3>

                        <div class="equation-box">
                            T{x(t − t₀)}
                            =
                            y(t − t₀),
                            &nbsp;
                            y(t)=T{x(t)}
                        </div>

                        <p>
                            Delaying the input before applying
                            the system must produce the same
                            delay in the output.
                        </p>

                    </article>

                </div>


                <section class="lti-requirement">

                    <h3>LTI Requirement</h3>

                    <div class="requirement-equation">
                        LTI = Linear AND Time-Invariant
                    </div>

                </section>


                <section class="concept-examples">

                    <div class="section-heading">

                        <div>
                            <span class="eyebrow">
                                EXPLORE
                            </span>

                            <h2>Examples</h2>
                        </div>

                        <p>
                            Use the interactive labs to test
                            these systems yourself.
                        </p>

                    </div>


                    <div class="example-grid">

                        <article class="example-card">
                            <span>01</span>
                            <h3>y(t) = 2x(t)</h3>
                            <p>
                                Linear and time-invariant.
                            </p>
                        </article>


                        <article class="example-card">
                            <span>02</span>
                            <h3>y(t) = x(t) + 1</h3>
                            <p>
                                Test the linearity condition.
                            </p>
                        </article>


                        <article class="example-card">
                            <span>03</span>
                            <h3>y(t) = x²(t)</h3>
                            <p>
                                Observe what happens when
                                the input is scaled.
                            </p>
                        </article>


                        <article class="example-card">
                            <span>04</span>
                            <h3>y(t) = x(t − 2)</h3>
                            <p>
                                Investigate the effect
                                of a fixed delay.
                            </p>
                        </article>


                        <article class="example-card">
                            <span>05</span>
                            <h3>y(t) = t x(t)</h3>
                            <p>
                                Test whether an explicit
                                dependence on time matters.
                            </p>
                        </article>


                        <article class="example-card">
                            <span>06</span>
                            <h3>y(t) = x(−t)</h3>
                            <p>
                                Explore time reversal
                                graphically.
                            </p>
                        </article>

                    </div>

                </section>

            </section>
        `;
    }


    /* -----------------------------------------------------
       TEMPORARY PLACEHOLDER
    ----------------------------------------------------- */

    function renderPlaceholder(
        container,
        title
    ) {

        container.innerHTML = `
            <section class="lab-placeholder">

                <span>
                    INTERACTIVE LAB
                </span>

                <h2>${title}</h2>

                <p>
                    This interactive module
                    will be implemented next.
                </p>

            </section>
        `;
    }


    /* -----------------------------------------------------
       PUBLIC API
    ----------------------------------------------------- */

    return {
        render
    };

})();
