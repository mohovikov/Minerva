/*!
 * Адаптированный Color mode toggler для FontAwesome
 */

(() => {
  "use strict";

  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };

  const setTheme = (theme) => {
    if (theme === "auto") {
      document.documentElement.setAttribute(
        "data-bs-theme",
        window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light",
      );
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }
  };

  setTheme(getPreferredTheme());

  const showActiveTheme = (theme, focus = false) => {
    const themeSwitcher = document.querySelector("#bd-theme");
    if (!themeSwitcher) return;

    const btnToActive = document.querySelector(
      `[data-bs-theme-value="${theme}"]`,
    );

    document.querySelectorAll("[data-bs-theme-value]").forEach((element) => {
      element.classList.remove("active");
      element.setAttribute("aria-pressed", "false");

      const checkIcon = element.querySelector(".fa-check");
      if (checkIcon) checkIcon.classList.add("d-none");
    });

    if (btnToActive) {
      btnToActive.classList.add("active");
      btnToActive.setAttribute("aria-pressed", "true");

      const checkIcon = btnToActive.querySelector(".fa-check");
      if (checkIcon) checkIcon.classList.remove("d-none");

      const triggerIcon = themeSwitcher.querySelector("i");
      if (triggerIcon) {
        const activeItemIcon = btnToActive.querySelector("i");
        if (activeItemIcon) {
          const iconClasses = activeItemIcon.className
            .split(" ")
            .filter((c) => c.startsWith("fa-"));
          triggerIcon.className = `fa-solid ${iconClasses.join(" ")}`;
        }
      }
    }

    if (focus) {
      themeSwitcher.focus();
    }
  };

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const storedTheme = getStoredTheme();
      if (storedTheme !== "light" && storedTheme !== "dark") {
        setTheme(getPreferredTheme());
      }
    });

  window.addEventListener("DOMContentLoaded", () => {
    showActiveTheme(getPreferredTheme());

    document.querySelectorAll("[data-bs-theme-value]").forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const theme = toggle.getAttribute("data-bs-theme-value");
        setStoredTheme(theme);
        setTheme(theme);
        showActiveTheme(theme, true);

        if (typeof renderStatsCharts === "function") {
          setTimeout(renderStatsCharts, 50);
        }
      });
    });
  });
})();
