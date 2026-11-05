document.addEventListener("DOMContentLoaded", function () {
  const copyButtons = document.querySelectorAll(".copy-btn");

  copyButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      this.blur();

      const textToCopy = this.getAttribute("data-clipboard-text");
      const icon = this.querySelector("i");
      const originalClass = icon.className;

      const textArea = document.createElement("textarea");
      textArea.value = textToCopy;

      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      textArea.style.top = "0";
      document.body.appendChild(textArea);

      textArea.focus();
      textArea.select();

      try {
        const successful = document.execCommand("copy");
        if (successful) {
          icon.className = "fa-solid fa-check";
        } else {
          icon.className = "fa-solid fa-xmark";
        }
      } catch (err) {
        console.error("Ошибка копирования: ", err);
        icon.className = "fa-solid fa-xmark";
      } finally {
        document.body.removeChild(textArea);
        setTimeout(() => {
          icon.className = originalClass;
        }, 2000);
      }
    });
  });
});
