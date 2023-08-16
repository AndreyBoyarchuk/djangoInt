// Replace the URL below with the actual path to your JSON file.
const dataUrl = "profitAndLossData";

fetch(dataUrl)
    .then(response => response.json())
    .then(data => {
        processData(data);
    })
    .catch(error => {
        console.error("Error loading data:", error);
    });
