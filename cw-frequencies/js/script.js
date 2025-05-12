import { createChart, addPoint, addBar } from './frequency-chart-library.js';

document.addEventListener("DOMContentLoaded", () => {
    function renderChart1() {
        // Clear the existing chart
        document.getElementById("chart1").innerHTML = "";

        const chart = createChart("chart1", [14000, 14150]);

        addBar(chart, 14060, 14065, "QRP Operations", 40);
        addPoint(chart, 14050, "Beginner QSOs", 10);
        addBar(chart, 14045, 14055, "Slower or Beginner CW", 95);
        addBar(chart, 14040, 14060, "SKCC", -80);
        addBar(chart, 14104, 14124, "SKCC Watering Hole", 15);
        addBar(chart, 14101, 14111, "Refuge During Contest Weekends", -35);
        addPoint(chart, 14047.5, "W1AW", 60);
        addBar(chart, 14071, 14074, "FT8 (No CW here)", -20);
        addBar(chart, 14028, 14045, "K1USN Weekly Slow Speed Test", -50);
        addBar(chart, 14000, 14030, "QRQ - Fast Code Here", 30);
        addBar(chart, 14000, 14020, "A lot of DX Stations", -20);
        addBar(chart, 14000, 14025, "Extra Class (US Amateurs)", -90);
        addBar(chart, 14052, 14062, "LICW Challenge", -110);
    }

    function renderChart2() {
        document.getElementById("chart2").innerHTML = "";

        const chart = createChart("chart2", [7000, 7150]);

        addBar(chart, 7030, 7035, "QRP Operations", 60);
        addPoint(chart, 7050, "Beginner QSOs", 10);
        addBar(chart, 7045, 7055, "Slower or Beginner CW", 95);
        addBar(chart, 7101, 7111, "Refuge During Contest Weekends", -35);
        addPoint(chart, 7047.5, "W1AW", 40);
        addBar(chart, 7071, 7074, "FT8 (No CW here)", -20);
        addBar(chart, 7028, 7045, "K1USN Weekly Slow Speed Test", -47);
        addBar(chart, 7000, 7030, "QRQ - Fast Code Here", 30);
        addBar(chart, 7000, 7020, "A lot of DX Stations", -20);
        addBar(chart, 7000, 7025, "Extra Class (US Amateurs)", -75);
        addBar(chart, 7052, 7062, "LICW (US)", -75);
        addBar(chart, 7032, 7042, "LICW (EU)", -105);

    }

    function renderChart3() {
        document.getElementById("chart3").innerHTML = "";

        const chart = createChart("chart3", [7020, 7160]);
        addBar(chart, 7028, 7048, "SKCC secondary", -30);
        addBar(chart, 7045, 7065, "SKCC primary", 15);
        addBar(chart, 7104, 7124, "SKCC Watering Hole", 15);
        addBar(chart, 7071, 7074, "FT8 (No CW here)", -20);
        addPoint(chart, 7114, "SKCC beginning operators", -25);
    }

    // Initial render
    renderChart1();

    // Re-render the chart on window resize
    window.addEventListener("resize", renderChart1);

    renderChart2();
    window.addEventListener("resize", renderChart2);

    renderChart3();
    window.addEventListener("resize", renderChart3);
});
