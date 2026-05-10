document.addEventListener("DOMContentLoaded", () => {
    const dataElement = document.getElementById("dashboard-data");

    if (!dataElement || typeof Chart === "undefined") {
        return;
    }

    const dashboardData = JSON.parse(dataElement.textContent);
    const salesCtx = document.getElementById("salesChart");
    const ordersCtx = document.getElementById("ordersChart");

    const textColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--text-muted")
        .trim() || "#94a3b8";

    const borderColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--border-color")
        .trim() || "rgba(255,255,255,.08)";

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "Inter, system-ui, sans-serif";

    if (salesCtx) {
        new Chart(salesCtx, {
            type: "line",
            data: {
                labels: dashboardData.sales.labels,
                datasets: [{
                    label: "Ventes",
                    data: dashboardData.sales.values,
                    borderColor: "#7c3aed",
                    backgroundColor: "rgba(124,58,237,.15)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: "#7c3aed"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: borderColor
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: borderColor
                        }
                    }
                }
            }
        });
    }

    if (ordersCtx) {
        new Chart(ordersCtx, {
            type: "doughnut",
            data: {
                labels: dashboardData.orders.labels,
                datasets: [{
                    data: dashboardData.orders.values,
                    backgroundColor: [
                        "#f59e0b",
                        "#06b6d4",
                        "#3b82f6",
                        "#10b981",
                        "#ef4444"
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "75%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: textColor
                        }
                    }
                }
            }
        });
    }
});
