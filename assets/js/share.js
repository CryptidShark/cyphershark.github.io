(() => {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = button.getAttribute("data-copy") || "";
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(value);
        button.textContent = "Enlace copiado";
      } catch {
        window.prompt("Copia este enlace para pegarlo en Instagram:", value);
        button.textContent = "Enlace listo";
      }
      window.setTimeout(() => {
        button.textContent = original;
      }, 2000);
    });
  });
})();
