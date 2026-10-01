/* =========================================================
   EE-207 SIGNALS & SYSTEMS
   Main Application Controller
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const navTabs = document.querySelectorAll(".nav-tab");
    const pages = document.querySelectorAll(".page");
    const moduleCards = document.querySelectorAll(".module-card.available");


    /* =====================================================
       PAGE NAVIGATION
       ===================================================== */

    function openPage(pageId) {

        // Hide every page
        pages.forEach((page) => {
            page.classList.remove("active");
        });

        // Remove active state from sidebar
        navTabs.forEach((tab) => {
            tab.classList.remove("active");
        });


        // Show requested page
        const targetPage = document.getElementById(pageId);

        if (!targetPage) {
            console.warn(`Page "${pageId}" was not found.`);
            return;
        }

        targetPage.classList.add("active");


        // Highlight corresponding sidebar tab
        const targetTab = document.querySelector(
            `.nav-tab[data-page="${pageId}"]`
        );

        if (targetTab) {
            targetTab.classList.add("active");
        }


        // Save current page
        localStorage.setItem(
            "ee207-current-page",
            pageId
        );


        // Return to top
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }


    /* =====================================================
       SIDEBAR BUTTONS
       ===================================================== */

    navTabs.forEach((tab) => {

        tab.addEventListener("click", () => {

            const pageId = tab.dataset.page;

            openPage(pageId);

        });

    });


    /* =====================================================
       HOME MODULE CARDS
       ===================================================== */

    moduleCards.forEach((card) => {

        card.addEventListener("click", () => {

            const pageId = card.dataset.open;

            if (pageId) {
                openPage(pageId);
            }

        });

    });


    /* =====================================================
       KEYBOARD ACCESSIBILITY
       ===================================================== */

    moduleCards.forEach((card) => {

        card.setAttribute("tabindex", "0");

        card.setAttribute(
            "role",
            "button"
        );


        card.addEventListener("keydown", (event) => {

            if (
                event.key === "Enter" ||
                event.key === " "
            ) {

                event.preventDefault();

                const pageId = card.dataset.open;

                if (pageId) {
                    openPage(pageId);
                }

            }

        });

    });


    /* =====================================================
       RESTORE LAST OPEN PAGE
       ===================================================== */

    const savedPage =
        localStorage.getItem(
            "ee207-current-page"
        );


    if (
        savedPage &&
        document.getElementById(savedPage)
    ) {

        openPage(savedPage);

    } else {

        openPage("home");

    }


    /* =====================================================
       APP READY
       ===================================================== */

    console.log(
        "EE-207 Signals & Systems web application loaded."
    );

});
