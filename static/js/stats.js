// График 1: Линейный
const ctx1 = document.getElementById("dailyChart").getContext("2d");
new Chart(ctx1, {
  type: "line",
  data: {
    labels: dates,
    datasets: [
      {
        label: "Загруженно артов",
        data: counts,
        borderColor: "#212529",
        backgroundColor: "rgba(33, 37, 41, 0.1)",
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
        },
      },
      y: { beginAtZero: true, ticks: { stepSize: 1 } },
    },
  },
});

// График 2: Топ моделей (Горизонтальный бар)
const ctx2 = document.getElementById("modelChart").getContext("2d");
new Chart(ctx2, {
  type: "bar",
  data: {
    labels: modelNames,
    datasets: [
      {
        label: "Количество артов",
        data: modelCounts,
        backgroundColor: [
          "#212529",
          "#495057",
          "#6c757d",
          "#adb5bd",
          "#dee2e6",
        ],
        borderRadius: 4,
      },
    ],
  },
  options: {
    indexAxis: "y",
    responsive: true,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: { stepSize: 1 },
      },
      y: {
        grid: { display: false },
      },
    },
  },
});

// График 3: Топ-10 тегов (Горизонтальный Bar Chart)
const ctx3 = document.getElementById("tagChart").getContext("2d");
new Chart(ctx3, {
  type: "bar",
  data: {
    labels: tagNames,
    datasets: [
      {
        label: "Использований",
        data: tagCounts,
        backgroundColor: "#343a40",
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
      x: { beginAtZero: true, ticks: { stepSize: 1 } },
      y: {
        grid: { display: false },
        ticks: {
          autoSkip: false,
          stepSize: 1,
        },
      },
    },
  },
});

// График 4: Разрешения
const ctx4 = document.getElementById("resChart").getContext("2d");
new Chart(ctx4, {
  type: "bar",
  data: {
    labels: resNames,
    datasets: [
      {
        label: "Количество артов",
        data: resCounts,
        backgroundColor: "#6c757d",
        borderRadius: 4,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { beginAtZero: true, ticks: { stepSize: 1 } },
    },
  },
});
