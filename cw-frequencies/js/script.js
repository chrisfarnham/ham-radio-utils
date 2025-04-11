import { createChart, addPoint, addBar } from './library.js';

document.addEventListener("DOMContentLoaded", () => {
    // Create the chart for the range [14000, 14150]
    const chart = createChart("chart", [14000, 14150]);

    // Add elements to the chart
    addBar(chart, 14060, 14065, "QRP Operations", 40);
    addPoint(chart, 14050, "Beginner QSOs", 10);
    addBar(chart, 14045, 14055, "Slower or Beginner CW", 95);
    addBar(chart, 14040, 14060, "SKCC", -75);
    addBar(chart, 14104, 14124, "SKCC Watering Hole", 15);
    addBar(chart, 14101, 14111, "Refuge During Contest Weekends", -25);
    addPoint(chart, 14047.5, "W1AW", 60);
    addBar(chart, 14071, 14074, "FT8 (No CW here)", -20);
    addBar(chart, 14028, 14045, "K1USN Weekly Slow Speed Test", -40);
    addBar(chart, 14000, 14030, "QRQ - Fast Code Here", 30);
    addBar(chart, 14000, 14020, "A lot of DX Stations", -20);
    addBar(chart, 14000, 14025, "Extra Class (US Amateurs)", -70);
});
