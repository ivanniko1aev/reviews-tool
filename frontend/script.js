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
                "api-key": "YOUR_API_KEY",
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

    const embedCode = `<iframe src="https://yourapi.com/embed?api_key=${apiKey}" width="500" height="400"></iframe>`;
document.getElementById("embed-code").value = embedCode;

});

// Sample reviews to show in carousel (can be dynamically loaded)
const reviews = [
    { author: "John Doe", rating: 5, content: "This is a sample review. Great service, highly recommended!" },
    { author: "Jane Smith", rating: 4, content: "Very good service, would definitely use again." },
    { author: "Alex Johnson", rating: 5, content: "Outstanding! They exceeded my expectations." },
    { author: "Emily Davis", rating: 4, content: "Good service, but there was a slight delay." },
    { author: "Michael Brown", rating: 5, content: "Fantastic job! Highly recommend them." }
];

async function displayReviews() {
    const apiKey = localStorage.getItem("api_key");
    const response = await fetch("/get-snippets/", {
        method: "GET",
        headers: { "api_key": apiKey }
    });

    if (response.ok) {
        const data = await response.json();
        const reviews = data.snippets;  // Get reviews from API
        const carousel = document.getElementById("review-carousel");
        carousel.innerHTML = ''; // Clear existing reviews

        reviews.forEach(review => {
            const reviewElement = document.createElement("div");
            reviewElement.classList.add("review");
            reviewElement.innerHTML = `
                <p>${review.embed_code}</p>
            `;
            carousel.appendChild(reviewElement);
        });
    } else {
        console.error("Failed to fetch reviews.");
    }
}


// Function to scroll carousel
function scrollCarousel(direction) {
    const carousel = document.getElementById("review-carousel");
    const scrollAmount = 320;  // Adjust this value for how far you want to scroll

    if (direction === 'next') {
        carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    } else {
        carousel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    }
}

// Wait for the DOM to be fully loaded before calling displayReviews
document.addEventListener('DOMContentLoaded', function() {
    displayReviews();
});

async function signupUser(email) {
    try {
        const response = await fetch("/signup/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("api_key", data.api_key);
            alert("Signup successful! Your API key is stored.");
        } else {
            alert("Signup failed. Try again.");
        }
    } catch (error) {
        console.error("Error during signup:", error);
        alert("Signup error. Please try again.");
    }
}

const apiKey = localStorage.getItem("api_key");  // Get stored API key

const response = await fetch("/scrape-reviews", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "api_key": apiKey || "" // Use stored API key
    },
    body: JSON.stringify({
        google_maps_url: googleUrl
    }),
});
