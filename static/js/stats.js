function getCssColor(variableName) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(variableName)
    .trim();
}

window.statsCharts = {};

function renderStatsCharts() {
  const colors = {
    line: getCssColor("--chart-line"),
    lineBg: getCssColor("--chart-line-bg"),
    text: getCssColor("--chart-text"),
    grid: getCssColor("--chart-grid"),
    bars: [
      getCssColor("--chart-bar-1"),
      getCssColor("--chart-bar-2"),
      getCssColor("--chart-bar-3"),
      getCssColor("--chart-bar-4"),
      getCssColor("--chart-bar-5"),
    ],
    barMain: getCssColor("--chart-bar-main"),
    barRes: getCssColor("--chart-bar-res"),
  };

  Object.values(window.statsCharts).forEach((chart) => {
    if (chart) chart.destroy();
  });
  window.statsCharts = {};

  // ==========================================
  // График 1: Генерация за последние 30 дней
  // ==========================================
  const ctx1 = document.getElementById("dailyChart").getContext("2d");
  window.statsCharts.daily = new Chart(ctx1, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: "Загруженно артов",
          data: counts,
          borderColor: colors.line,
          backgroundColor: colors.lineBg,
          borderWidth: 2,
          tension: 0.3,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45,
            autoSkip: true,
            color: colors.text,
          },
          grid: { color: colors.grid },
        },
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: colors.text },
          grid: { color: colors.grid },
        },
      },
    },
  });

  // ==========================================
  // График 2: Топ-5 моделей
  // ==========================================
  const ctx2 = document.getElementById("modelChart").getContext("2d");
  window.statsCharts.model = new Chart(ctx2, {
    type: "bar",
    data: {
      labels: modelNames,
      datasets: [
        {
          label: "Количество артов",
          data: modelCounts,
          backgroundColor: colors.bars,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: colors.text },
          grid: { color: colors.grid },
        },
        y: { grid: { display: false }, ticks: { color: colors.text } },
      },
    },
  });

  // ==========================================
  // График 3: Топ-15 Positive тегов
  // ==========================================
  const ctxPos3 = document.getElementById("posTagChart").getContext("2d");
  new Chart(ctxPos3, {
    type: "bar",
    data: {
      labels: posTagNames,
      datasets: [
        {
          label: "Использований",
          data: posTagCounts,
          backgroundColor: colors.barMain,
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: colors.text },
          grid: { color: colors.grid },
        },
        y: {
          grid: { display: false },
          ticks: { autoSkip: false, font: { size: 11 }, color: colors.text },
        },
      },
      onClick: (e, activeElements) => {
        if (activeElements.length > 0) {
          const index = activeElements[0].index;
          const tagName = posTagNames[index];
          window.location.href = `/?q=${encodeURIComponent(tagName)}`;
        }
      },
      onHover: (event, activeElements) => {
        event.native.target.style.cursor =
          activeElements.length > 0 ? "pointer" : "default";
      },
    },
  });

  // ==========================================
  // График 4: Топ-15 Negative тегов
  // ==========================================
  const ctxNeg4 = document.getElementById("negTagChart").getContext("2d");
  new Chart(ctxNeg4, {
    type: "bar",
    data: {
      labels: negTagNames,
      datasets: [
        {
          label: "Использований",
          data: negTagCounts,
          backgroundColor: "#dc3545",
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: colors.text },
          grid: { color: colors.grid },
        },
        y: {
          grid: { display: false },
          ticks: { autoSkip: false, font: { size: 11 }, color: colors.text },
        },
      },
      onClick: (e, activeElements) => {
        if (activeElements.length > 0) {
          const index = activeElements[0].index;
          const tagName = negTagNames[index];
          window.location.href = `/?q=${encodeURIComponent(tagName)}`;
        }
      },
      onHover: (event, activeElements) => {
        event.native.target.style.cursor =
          activeElements.length > 0 ? "pointer" : "default";
      },
    },
  });

  // ==========================================
  // График 5: Топ-5 разрешений
  // ==========================================
  const ctx5 = document.getElementById("resChart").getContext("2d");
  window.statsCharts.res = new Chart(ctx5, {
    type: "bar",
    data: {
      labels: resNames,
      datasets: [
        {
          label: "Количество артов",
          data: resCounts,
          backgroundColor: colors.bars,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: colors.text } },
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: colors.text },
          grid: { color: colors.grid },
        },
      },
    },
  });
}

// 🎯 Первый запуск при загрузке страницы
document.addEventListener("DOMContentLoaded", renderStatsCharts);
