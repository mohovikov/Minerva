// Функция для получения цвета из CSS
function getCssColor(variableName) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(variableName)
    .trim();
}

// Глобальный объект для хранения экземпляров графиков (чтобы их можно было уничтожить)
window.statsCharts = {};

function renderStatsCharts() {
  // 1. Получаем актуальные цвета (каждый раз при вызове)
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

  // 2. Уничтожаем старые графики, если они существуют
  Object.values(window.statsCharts).forEach((chart) => {
    if (chart) chart.destroy();
  });
  window.statsCharts = {}; // Очищаем объект

  // 3. Создаем графики заново
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
      indexAxis: "y",
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

  const ctx3 = document.getElementById("tagChart").getContext("2d");
  window.statsCharts.tag = new Chart(ctx3, {
    type: "bar",
    data: {
      labels: tagNames,
      datasets: [
        {
          label: "Использований",
          data: tagCounts,
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
          ticks: { autoSkip: false, stepSize: 1, color: colors.text },
        },
      },
    },
  });

  const ctx4 = document.getElementById("resChart").getContext("2d");
  window.statsCharts.res = new Chart(ctx4, {
    type: "bar",
    data: {
      labels: resNames,
      datasets: [
        {
          label: "Количество артов",
          data: resCounts,
          backgroundColor: colors.barRes,
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
