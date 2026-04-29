let chart = null;
const API = "";

async function loadCompanies() {
    console.log("loadCompanies called");
    try {
        const url = `${window.location.origin}/api/companies`;
        console.log("Fetching from:", url);
        const res = await fetch(url);
        console.log("Response status:", res.status);
        const data = await res.json();
        console.log("Data received:", data);
        const select = document.getElementById("company-select");
        select.innerHTML = "";
        data.companies.forEach(c => {
            const opt = document.createElement("option");
            opt.value = c;
            opt.textContent = c;
            select.appendChild(opt);
        });
        console.log("Dropdown populated");
    } catch (e) {
        console.error("Could not load companies:", e);
    }
}

async function analyze() {
    const company = document.getElementById("company-select").value;

    document.getElementById("ndi-score").textContent = "...";
    document.getElementById("ndi-level").textContent = "loading";
    document.getElementById("mean-sentiment").textContent = "...";
    document.getElementById("outlet-count").textContent = "...";
    document.getElementById("markets-list").innerHTML =
        '<p class="empty">Loading markets...</p>';
    document.getElementById("outlet-breakdown").innerHTML = "";
    document.getElementById("prediction-box").innerHTML =
        '<p class="empty">Loading prediction...</p>';

    await loadNDI(company);
    await loadMarkets(company);
    await loadPrediction(company);
}

async function loadNDI(company) {
    try {
        const res = await fetch(`${window.location.origin}/api/ndi/${company}`);
        const data = await res.json();

        if (!data.history.length) {
            document.getElementById("ndi-score").textContent = "No data";
            document.getElementById("ndi-level").textContent = "no headlines found";
            document.getElementById("mean-sentiment").textContent = "—";
            document.getElementById("outlet-count").textContent = "—";
            return;
        }

        const latest = data.history[0];

        const ndiEl = document.getElementById("ndi-score");
        ndiEl.textContent = latest.ndi_score.toFixed(3);
        ndiEl.className = "card-value " + latest.disagreement_level;

        document.getElementById("ndi-level").textContent =
            latest.disagreement_level + " disagreement";

        const sentEl = document.getElementById("mean-sentiment");
        const sentVal = latest.mean_sentiment;
        sentEl.textContent = (sentVal >= 0 ? "+" : "") + sentVal.toFixed(3);
        sentEl.className = "card-value " +
            (sentVal > 0.05 ? "positive" : sentVal < -0.05 ? "negative" : "neutral");

        document.getElementById("outlet-count").textContent =
            latest.outlet_count || "—";

        const labels = data.history.map(d => d.date).reverse();
        const scores = data.history.map(d => d.ndi_score).reverse();
        const sentiments = data.history.map(d => d.mean_sentiment).reverse();

        if (chart) chart.destroy();

        chart = new Chart(document.getElementById("ndi-chart"), {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "NDI Score",
                        data: scores,
                        borderColor: "#00ff88",
                        backgroundColor: function(context) {
                            const ch = context.chart;
                            const { ctx, chartArea } = ch;
                            if (!chartArea) return "transparent";
                            const gradient = ctx.createLinearGradient(
                                0, chartArea.top, 0, chartArea.bottom
                            );
                            gradient.addColorStop(0, "rgba(0,255,136,0.25)");
                            gradient.addColorStop(1, "rgba(0,255,136,0)");
                            return gradient;
                        },
                        borderWidth: 2,
                        pointBackgroundColor: "#00ff88",
                        pointBorderColor: "#050508",
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: "#00ff88",
                        pointHoverBorderColor: "#fff",
                        tension: 0.4,
                        fill: true,
                        yAxisID: "y"
                    },
                    {
                        label: "Mean Sentiment",
                        data: sentiments,
                        borderColor: "#4488ff",
                        backgroundColor: function(context) {
                            const ch = context.chart;
                            const { ctx, chartArea } = ch;
                            if (!chartArea) return "transparent";
                            const gradient = ctx.createLinearGradient(
                                0, chartArea.top, 0, chartArea.bottom
                            );
                            gradient.addColorStop(0, "rgba(68,136,255,0.2)");
                            gradient.addColorStop(1, "rgba(68,136,255,0)");
                            return gradient;
                        },
                        borderWidth: 2,
                        pointBackgroundColor: "#4488ff",
                        pointBorderColor: "#050508",
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: "#4488ff",
                        pointHoverBorderColor: "#fff",
                        tension: 0.4,
                        fill: true,
                        yAxisID: "y"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: {
                        display: true,
                        position: "top",
                        align: "end",
                        labels: {
                            color: "#444",
                            font: { family: "Courier New", size: 10 },
                            boxWidth: 8,
                            boxHeight: 8,
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: "circle"
                        }
                    },
                    tooltip: {
                        backgroundColor: "#0a0a12",
                        borderColor: "#1a1a2a",
                        borderWidth: 1,
                        titleColor: "#555",
                        bodyColor: "#ccc",
                        titleFont: { family: "Courier New", size: 10 },
                        bodyFont: { family: "Courier New", size: 12 },
                        padding: 14,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const val = context.parsed.y;
                                const sign = val >= 0 ? "+" : "";
                                return `  ${context.dataset.label}: ${sign}${val.toFixed(4)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: "#333",
                            font: { family: "Courier New", size: 10 },
                            maxRotation: 0,
                            maxTicksLimit: 10
                        },
                        grid: { color: "#0a0a12" },
                        border: { color: "#1a1a2a" }
                    },
                    y: {
                        ticks: {
                            color: "#333",
                            font: { family: "Courier New", size: 10 },
                            callback: function(val) { return val.toFixed(2); }
                        },
                        grid: { color: "#0f0f18" },
                        border: { color: "#1a1a2a" }
                    }
                }
            }
        });

    } catch (e) {
        console.error("NDI load error:", e);
        document.getElementById("ndi-score").textContent = "Error";
    }
}

async function loadMarkets(company) {
    try {
        const res = await fetch(
            `${window.location.origin}/api/markets/${encodeURIComponent(company)}`
        );
        const data = await res.json();
        const list = document.getElementById("markets-list");
        list.innerHTML = "";

        if (!data.markets || !data.markets.length) {
            list.innerHTML = '<p class="empty">No related prediction markets found</p>';
            return;
        }

        data.markets.forEach(m => {
            const row = document.createElement("div");
            row.className = "market-row";
            row.innerHTML = `
                <div>
                    <div class="market-source">${m.source}</div>
                    <div class="market-title">${m.title}</div>
                </div>
                <div class="market-odds">
                    <span class="yes">YES ${m.yes_price}¢</span>
                    <span class="no">NO ${m.no_price}¢</span>
                </div>
            `;
            list.appendChild(row);
        });

    } catch (e) {
        console.error("Markets load error:", e);
        document.getElementById("markets-list").innerHTML =
            '<p class="empty">Could not load markets</p>';
    }
}

async function loadPrediction(company) {
    try {
        const res = await fetch(
            `${window.location.origin}/api/predict/${encodeURIComponent(company)}`
        );
        const d = await res.json();

        if (d.error) {
            document.getElementById("prediction-box").innerHTML =
                `<p class="empty">${d.error}</p>`;
            return;
        }

        const isUp = d.price_change_7d >= 0;
        const signalClass =
            d.prediction.includes("BULLISH") ? "bullish" :
            d.prediction.includes("BEARISH") ? "bearish" : "neutral-signal";

        const changeClass = isUp ? "change-up" : "change-down";
        const changeSymbol = isUp ? "▲" : "▼";

        const signals = d.signals;

        document.getElementById("prediction-box").innerHTML = `
            <div class="prediction-header">
                <div>
                    <div class="prediction-label">7-Day Signal</div>
                    <div class="prediction-signal ${signalClass}">
                        ${d.prediction}
                    </div>
                    <div class="prediction-confidence">
                        ${signals.signal_score > 0 ? "+" : ""}${signals.signal_score} confidence score
                    </div>
                </div>
                <div class="prediction-price">
                    <div class="prediction-label">${d.ticker} Current Price</div>
                    <div class="prediction-current">$${d.current_price}</div>
                    <div class="prediction-change ${changeClass}">
                        ${changeSymbol} ${Math.abs(d.price_change_7d)}% past 7 days
                    </div>
                </div>
            </div>

            <div class="prediction-summary">${d.summary}</div>

            <div class="prediction-range">
                <div class="range-box">
                    <div class="range-label">Predicted Low (7d)</div>
                    <div class="range-value bearish">$${d.predicted_range.low}</div>
                </div>
                <div class="range-box">
                    <div class="range-label">Predicted High (7d)</div>
                    <div class="range-value bullish">$${d.predicted_range.high}</div>
                </div>
            </div>

            <div class="prediction-signals">
                <div class="signal-box">
                    <div class="signal-label">NDI Score</div>
                    <div class="signal-value ${
                        signals.ndi_score > 0.25 ? "bearish" :
                        signals.ndi_score < 0.1 ? "bullish" : "neutral-signal"
                    }">${signals.ndi_score}</div>
                </div>
                <div class="signal-box">
                    <div class="signal-label">Sentiment</div>
                    <div class="signal-value ${
                        signals.sentiment > 0.05 ? "bullish" :
                        signals.sentiment < -0.05 ? "bearish" : "neutral-signal"
                    }">${signals.sentiment > 0 ? "+" : ""}${signals.sentiment}</div>
                </div>
                <div class="signal-box">
                    <div class="signal-label">Price Trend</div>
                    <div class="signal-value ${
                        signals.price_trend === "up" ? "bullish" : "bearish"
                    }">${signals.price_trend.toUpperCase()}</div>
                </div>
            </div>
        `;

    } catch (e) {
        console.error("Prediction error:", e);
        document.getElementById("prediction-box").innerHTML =
            '<p class="empty">Could not load prediction</p>';
    }
}

document.getElementById("analyze-btn").addEventListener("click", analyze);
loadCompanies();