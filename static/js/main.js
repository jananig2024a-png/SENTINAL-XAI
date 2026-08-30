/* ==========================================
   SentinelXAI - main.js
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    /* ==========================
       Navbar Shadow
    ========================== */

    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", () => {

        if (window.scrollY > 30) {

            navbar.style.boxShadow = "0 10px 25px rgba(15,23,42,0.08)";

        } else {

            navbar.style.boxShadow = "none";

        }

    });

    /* ==========================
       Counter Animation
    ========================== */

    const counters = document.querySelectorAll(".stat-card h2");

    const speed = 120;

    counters.forEach(counter => {

        const targetText = counter.innerText;

        const numeric = parseFloat(targetText);

        if (isNaN(numeric)) return;

        let current = 0;

        const increment = numeric / speed;

        function updateCounter() {

            if (current < numeric) {

                current += increment;

                if (targetText.includes("%")) {

                    counter.innerText = current.toFixed(2) + "%";

                }
                else if (targetText.includes("+")) {

                    counter.innerText = Math.floor(current) + "+";

                }
                else {

                    counter.innerText = Math.floor(current);

                }

                requestAnimationFrame(updateCounter);

            }
            else {

                counter.innerText = targetText;

            }

        }

        updateCounter();

    });

    /* ==========================
       Fade In Animation
    ========================== */

    const observer = new IntersectionObserver(entries => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.classList.add("show");

            }

        });

    }, {

        threshold: 0.15

    });

    const hiddenElements = document.querySelectorAll(

        ".hero-content,.hero-image,.stat-card,.feature-card,.why-content,.why-image"

    );

    hiddenElements.forEach(el => {

        el.classList.add("hidden");

        observer.observe(el);

    });

    /* ==========================
       Active Navigation
    ========================== */

    const currentPage = window.location.pathname;

    document.querySelectorAll(".nav-links a").forEach(link => {

        if (link.getAttribute("href") === currentPage) {

            link.classList.add("active-link");

        }

    });

});

/* ==========================
   Scroll To Top Button
========================== */

const scrollBtn = document.createElement("button");

scrollBtn.innerHTML = "↑";

scrollBtn.id = "scrollTopBtn";

document.body.appendChild(scrollBtn);

scrollBtn.style.position = "fixed";
scrollBtn.style.right = "25px";
scrollBtn.style.bottom = "25px";
scrollBtn.style.width = "50px";
scrollBtn.style.height = "50px";
scrollBtn.style.borderRadius = "50%";
scrollBtn.style.border = "none";
scrollBtn.style.cursor = "pointer";
scrollBtn.style.fontSize = "20px";
scrollBtn.style.background = "#0EA5A4";
scrollBtn.style.color = "#fff";
scrollBtn.style.display = "none";
scrollBtn.style.boxShadow = "0 8px 20px rgba(0,0,0,.15)";
scrollBtn.style.transition = ".3s";

window.addEventListener("scroll", () => {

    if (window.scrollY > 300) {

        scrollBtn.style.display = "block";

    }
    else {

        scrollBtn.style.display = "none";

    }

});

scrollBtn.addEventListener("click", () => {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

});