/* =========================================================
   EE-207 SIGNALS & SYSTEMS
   Main Application Controller
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       DOM REFERENCES
       ===================================================== */

    const navTabs =
        document.querySelectorAll(".nav-tab");

    const pages =
        document.querySelectorAll(".page");

    const moduleCards =
        document.querySelectorAll(
            ".module-card.available"
        );


    /* =====================================================
       PAGE NAVIGATION
       ===================================================== */

    function openPage(pageId) {

        /* ---------------------------------------------
           Find requested page
        --------------------------------------------- */

        const targetPage =
            document.getElementById(pageId);


        if (!targetPage) {

            console.warn(
                `Page "${pageId}" was not found.`
            );

            return;
        }


        /* ---------------------------------------------
           Hide all pages
        --------------------------------------------- */

        pages.forEach((page) => {

            page.classList.remove("active");

        });


        /* ---------------------------------------------
           Remove active state from sidebar
        --------------------------------------------- */

        navTabs.forEach((tab) => {

            tab.classList.remove("active");

        });


        /* ---------------------------------------------
           Show selected page
        --------------------------------------------- */

        targetPage.classList.add("active");


        /* ---------------------------------------------
           Initialize chapter modules
        --------------------------------------------- */

        initializeChapter(pageId);


        /* ---------------------------------------------
           Highlight corresponding sidebar tab
        --------------------------------------------- */

        const targetTab =
            document.querySelector(
                `.nav-tab[data-page="${pageId}"]`
            );


        if (targetTab) {

            targetTab.classList.add("active");

        }


        /* ---------------------------------------------
           Remember current page
        --------------------------------------------- */

        try {

            localStorage.setItem(
                "ee207-current-page",
                pageId
            );

        } catch (error) {

            console.warn(
                "Local storage is not available."
            );

        }


        /* ---------------------------------------------
           Return to top
        --------------------------------------------- */

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    /* =====================================================
       CHAPTER INITIALIZATION
       ===================================================== */

    function initializeChapter(pageId) {

        switch (pageId) {

            /* -----------------------------------------
               LTI SYSTEMS
            ----------------------------------------- */

            case "lti":

                if (
                    typeof LTI !== "undefined" &&
                    typeof LTI.render === "function"
                ) {

                    LTI.render();

                } else {

                    console.warn(
                        "LTI module is not available."
                    );

                }

                break;


            /* -----------------------------------------
               CONVOLUTION

               Will be connected later.
            ----------------------------------------- */

            case "convolution":

                /*
                Future:

                if (
                    typeof Convolution !== "undefined" &&
                    typeof Convolution.render === "function"
                ) {
                    Convolution.render();
                }
                */

                break;


            /* -----------------------------------------
               FUTURE CHAPTERS
            ----------------------------------------- */

            case "laplace":
            case "fourier":
            case "filters":
            case "sampling":

                break;


            default:

                break;

        }

    }


    /* =====================================================
       SIDEBAR NAVIGATION
       ===================================================== */

    navTabs.forEach((tab) => {

        tab.addEventListener(
            "click",
            () => {

                const pageId =
                    tab.dataset.page;


                if (pageId) {

                    openPage(pageId);

                }

            }
        );

    });


    /* =====================================================
       HOME MODULE CARDS
       ===================================================== */

    moduleCards.forEach((card) => {

        card.addEventListener(
            "click",
            () => {

                const pageId =
                    card.dataset.open;


                if (pageId) {

                    openPage(pageId);

                }

            }
        );

    });


    /* =====================================================
       KEYBOARD ACCESSIBILITY
       ===================================================== */

    moduleCards.forEach((card) => {

        card.setAttribute(
            "tabindex",
            "0"
        );


        card.setAttribute(
            "role",
            "button"
        );


        card.addEventListener(
            "keydown",
            (event) => {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();


                    const pageId =
                        card.dataset.open;


                    if (pageId) {

                        openPage(pageId);

                    }

                }

            }
        );

    });


    /* =====================================================
       RESTORE PREVIOUS PAGE
       ===================================================== */

    function restorePage() {

        let savedPage = null;


        try {

            savedPage =
                localStorage.getItem(
                    "ee207-current-page"
                );

        } catch (error) {

            savedPage = null;

        }


        if (
            savedPage &&
            document.getElementById(savedPage)
        ) {

            openPage(savedPage);

        } else {

            openPage("home");

        }

    }


    /* =====================================================
       PUBLIC NAVIGATION EVENT

       Other modules will be able to request navigation
       without directly manipulating the page structure.
       ===================================================== */

    window.addEventListener(
        "ee207:navigate",
        (event) => {

            const pageId =
                event.detail?.page;


            if (pageId) {

                openPage(pageId);

            }

        }
    );


    /* =====================================================
       START APPLICATION
       ===================================================== */

    restorePage();


    console.log(
        "EE-207 Signals & Systems web application loaded."
    );

});
