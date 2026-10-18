"use strict";
const startLink = document.querySelector(".enter-link");
startLink?.addEventListener("click", (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)
        return;
    event.preventDefault();
    document.body.classList.add("leaving");
    window.setTimeout(() => { window.location.assign(startLink.href); }, 180);
});
