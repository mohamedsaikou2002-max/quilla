const startLink = document.querySelector<HTMLAnchorElement>(".enter-link");

startLink?.addEventListener("click", (event: MouseEvent) => {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  document.body.classList.add("leaving");
  window.setTimeout(() => { window.location.assign(startLink.href); }, 180);
});
