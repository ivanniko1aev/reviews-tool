// Sample review to show when the page first loads
const sampleReview = {
    author: "John Doe",
    rating: 5,
    content: "This is a sample review. Great service, highly recommended!"
};

// Initial display of the sample review in the preview container
function displaySampleReview() {
    const preview = document.getElementById("preview");
    preview.style.backgroundColor = '#ffffff'; // Default background color
    preview.style.color = '#000000'; // Default text color
    preview.innerHTML = `
        <div class="review">
            <h3>${sampleReview.author} (${sampleReview.rating})</h3>
            <p>${sampleReview.content}</p>
        </div>
    `;
}

// Update preview with selected colors and review data
function updatePreview(bgColor, textColor, review) {
    const preview = document.getElementById("preview");
    preview.style.backgroundColor = bgColor;
    preview.style.color = textColor;

    preview.innerHTML = `
        <div class="review">
            <h3>${review.author} (${review.rating})</h3>
            <p>${review.content}</p>
        </div>
    `;
}

// Call displaySampleReview on page load to show the default review
document.addEventListener('DOMContentLoaded', () => {
    displaySampleReview();
});

// Handle the "scrape reviews" button click
document.getElementById("scrape-btn").addEventListener("click", async () => {
    const googleUrl = document.getElementById("google-url").value.trim();

    if (!googleUrl) {
        alert("Please enter a valid Google Maps URL.");
        return;
    }

    const maxReviews = 10; // Default number of reviews
    const loadingElement = document.getElementById("loading");
    if (loadingElement) {
        loadingElement.style.display = "block";
    }

    try {
        const response = await fetch("/scrape-reviews", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                google_maps_url: googleUrl,
                max_reviews: maxReviews,
            }),
        });

        if (loadingElement) {
            loadingElement.style.display = "none";
        }

        if (response.ok) {
            const result = await response.json();
            const reviewsContainer = document.querySelector(".review-carousel");
            reviewsContainer.innerHTML = ""; // Clear previous reviews

            // Assuming you get an array of reviews from the API
            const reviews = result.reviews;

            // For the preview, let's show the first review
            if (reviews.length > 0) {
                const review = reviews[0]; // Use the first review from the scraped data
                updatePreview(document.getElementById('bg-color').value, document.getElementById('text-color').value, review);
            }
        } else {
            alert("Failed to scrape reviews. Please try again later.");
        }
    } catch (error) {
        alert("Error scraping reviews.");
        console.error(error);
    }
});

// Handle the selection of color from the color boxes for background color
document.querySelectorAll('.color-box-bg').forEach(function(box) {
    box.addEventListener('click', function() {
        const color = box.getAttribute('data-color');
        document.getElementById('bg-color').value = color;
        updatePreview(color, document.getElementById('text-color').value, sampleReview); // Use sample review for initial state
    });
});

// Handle the selection of color from the color boxes for font color
document.querySelectorAll('.color-box-text').forEach(function(box) {
    box.addEventListener('click', function() {
        const color = box.getAttribute('data-color');
        document.getElementById('text-color').value = color;
        updatePreview(document.getElementById('bg-color').value, color, sampleReview); // Use sample review for initial state
    });
});

// Handle the customization form submission (font and colors)
document.getElementById("customization-form").addEventListener("submit", function(e) {
    e.preventDefault();

    const font = document.getElementById("font").value;
    const fontSize = document.getElementById("font-size").value;
    const bgColor = document.getElementById("bg-color").value;
    const textColor = document.getElementById("text-color").value;

    updatePreview(bgColor, textColor, sampleReview); // Use sample review for initial state

    const embedCode = `<iframe src="https://yourwebsite.com/reviews/embedded?font=${font}&font-size=${fontSize}&bg-color=${bgColor}&text-color=${textColor}" width="500" height="400"></iframe>`;
    document.getElementById("embed-code").value = embedCode;
});
