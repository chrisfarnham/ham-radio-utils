// Define constants for font size control
const BASE_FONT_SIZE_MULTIPLIER = 0.015; // Adjust this value to control the default font size scaling
const MIN_FONT_SIZE = 8; // Minimum font size to ensure readability
const MAX_FONT_SIZE = 12; // Maximum font size to prevent overly large text

export function createChart(containerId, xDomain) {
    const chartElement = document.getElementById(containerId);

    // Get the width and height of the containing <div>
    const width = chartElement.clientWidth; // Width of the container
    const height = chartElement.clientHeight; // Height of the container

    const margin = { top: 20, right: 20, bottom: 50, left: 50 };

    // Define a constant for the x-axis scale
    const xScale = d3.scaleLinear()
        .domain(xDomain) // Input range for the frequency spectrum
        .range([margin.left, width - margin.right]); // Output range

    // Define a color scale for shapes
    const colorScale = d3.scaleLinear()
        .domain(xDomain) // Input range for the frequency spectrum
        .range(["red", "blue"]); // Color range

    // Create the SVG container
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Create the x-axis
    const xAxis = d3.axisBottom(xScale)
        .tickFormat(d => `${d} kHz`); // Format ticks to display "kHz"

    // Append the x-axis to the SVG, centered vertically
    svg.append("g")
        .attr("transform", `translate(0, ${height / 2})`) // Center the axis vertically
        .call(xAxis);

    return { svg, xScale, colorScale, height, width };
}

export function addPoint(chart, frequency, label, yOffset) {
    const { svg, xScale, colorScale, height, width } = chart;
    const y = height / 2 - yOffset; // Calculate the final y position using height and yOffset

    // Dynamically calculate font size based on chart width
    const fontSize = Math.min(
        Math.max(MIN_FONT_SIZE, width * BASE_FONT_SIZE_MULTIPLIER),
        MAX_FONT_SIZE
    ); // Ensure font size is between MIN_FONT_SIZE and MAX_FONT_SIZE

    // Add the circle for the point
    svg.append("circle")
        .attr("r", 5) // Radius of the circle
        .attr("fill", colorScale(frequency)) // Use the color scale for the circle color
        .attr("cx", xScale(frequency)) // Position on the x-axis
        .attr("cy", y); // Position on the y-axis

    // Add the label for the point
    const labelY = yOffset < 0 ? y + 15 : y - 10; // Position below if yOffset is negative, above otherwise
    const fullLabel = `${frequency} kHz - ${label}`; // Append frequency to the label
    svg.append("text")
        .attr("x", xScale(frequency)) // Position on the x-axis
        .attr("y", labelY) // Position based on yOffset
        .attr("text-anchor", "middle") // Center the text horizontally
        .attr("font-size", `${fontSize}px`) // Dynamically set font size
        .attr("fill", "black") // Text color
        .text(fullLabel); // Label text
}

export function addBar(chart, startFrequency, endFrequency, label, yOffset) {
    const { svg, xScale, colorScale, height, width } = chart;
    const y = height / 2 - yOffset; // Calculate the final y position using height and yOffset

    // Dynamically calculate font size based on chart width
    const fontSize = Math.min(
        Math.max(MIN_FONT_SIZE, width * BASE_FONT_SIZE_MULTIPLIER),
        MAX_FONT_SIZE
    ); // Ensure font size is between MIN_FONT_SIZE and MAX_FONT_SIZE

    // Add the rectangle for the frequency range
    svg.append("rect")
        .attr("x", xScale(startFrequency)) // Start position on the x-axis
        .attr("y", y) // Use the calculated y value
        .attr("width", xScale(endFrequency) - xScale(startFrequency)) // Width based on the frequency range
        .attr("height", 10) // Height of the bar
        .attr("fill", colorScale((startFrequency + endFrequency) / 2)) // Use the color scale for the bar color
        .attr("opacity", 0.7) // Slight transparency
        .attr("rx", 5) // Rounded corners on the x-axis
        .attr("ry", 5); // Rounded corners on the y-axis

    // Add the label for the rectangular bar
    const labelY = yOffset < 0 ? y + 25 : y - 6; // Position below if yOffset is negative, above otherwise
    const fullLabel = `${startFrequency}-${endFrequency} kHz - ${label}`; // Append frequencies to the label
    svg.append("text")
        .attr("x", (xScale(startFrequency) + xScale(endFrequency)) / 2) // Center the label in the bar
        .attr("y", labelY) // Position based on yOffset
        .attr("text-anchor", "middle") // Center the text horizontally
        .attr("font-size", `${fontSize}px`) // Dynamically set font size
        .attr("fill", "black") // Text color
        .text(fullLabel); // Label text
}
