// Function to handle Image Generation
function generateImage() {
    let type = document.getElementById("imageType").value;
    let prompt = document.getElementById("textPrompt").value;
    let outputDiv = document.getElementById("imageOutput");

    outputDiv.innerHTML = `<p>Generating Image for: ${prompt}...</p>`;
    
    fetch("/generate_image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: type, prompt: prompt })
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.innerHTML = `<img src="${data.image_url}" width="300">`;
    });
}

// Function to fetch Outfit Recommendations
function getOutfits() {
    let gender = document.getElementById("gender").value;
    let query = document.getElementById("query").value;
    let numResults = document.getElementById("numResults").value;
    let resultsDiv = document.getElementById("outfitResults");

    resultsDiv.innerHTML = `<p>Fetching recommendations...</p>`;

    fetch(`/recommend_outfits?gender=${gender}&query=${query}&num_results=${numResults}`)
    .then(response => response.json())
    .then(data => {
        resultsDiv.innerHTML = "";
        data.forEach(image => {
            let imgElement = document.createElement("img");
            imgElement.src = image;
            imgElement.width = 150;
            resultsDiv.appendChild(imgElement);
        });
    });
}
