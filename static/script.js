// Call displaySampleReview on page load to show the default review
document.addEventListener('DOMContentLoaded', () => {
    displaySampleReview();
    checkUserAuth();
    displayReviews();
});

// Handle the "scrape reviews" button click
document.getElementById("scrape-btn").addEventListener("click", async () => {
    const googleUrl = document.getElementById("google-url").value.trim();
    const apiKey = localStorage.getItem("api_key");

    if (!apiKey) {
        alert("You need to sign up first.");
        return;
    }

    if (!googleUrl) {
        alert("Please enter a valid Google Maps URL.");
        return;
    }

    const loadingElement = document.getElementById("loading");
    if (loadingElement) {
        loadingElement.style.display = "block";
    }

    try {
        const response = await fetch("/scrape-reviews", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "api_key": apiKey
            },
            body: JSON.stringify({
                google_maps_url: googleUrl
            }),
        });

        if (loadingElement) {
            loadingElement.style.display = "none";
        }

        if (response.ok) {
            const result = await response.json();
            alert("Reviews scraped successfully!");
        } else {
            alert("Failed to scrape reviews. Please try again later.");
        }
    } catch (error) {
        alert("Error scraping reviews.");
        console.error(error);
    }
});

document.addEventListener("DOMContentLoaded", () => {
    checkUserAuth(); // Check if user is already logged in
});

// Handle login button click - Show the signup modal
document.getElementById("login-btn").addEventListener("click", () => {
    document.getElementById("signup-modal").style.display = "block";
});

// Handle signup form submission
document.getElementById("signup-submit").addEventListener("click", async () => {
    const email = document.getElementById("signup-email").value.trim();
    
    if (!email) {
        document.getElementById("signup-message").innerText = "Please enter a valid email.";
        return;
    }

    try {
        const response = await fetch("/signup/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email }),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("api_key", data.api_key);
            document.getElementById("signup-message").innerText = "Signup successful! API key stored.";
            
            // Hide modal & update UI
            document.getElementById("signup-modal").style.display = "none";
            checkUserAuth();
        } else {
            document.getElementById("signup-message").innerText = "Signup failed. Try again.";
        }
    } catch (error) {
        console.error("Error during signup:", error);
        document.getElementById("signup-message").innerText = "Error signing up. Please try again.";
    }
});

// Logout function
document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("api_key");
    alert("Logged out successfully.");
    checkUserAuth();
});

// Check user authentication status
function checkUserAuth() {
    const apiKey = localStorage.getItem("api_key");

    if (apiKey) {
        document.getElementById("login-btn").style.display = "none";
        document.getElementById("logout-btn").style.display = "block";
    } else {
        document.getElementById("login-btn").style.display = "block";
        document.getElementById("logout-btn").style.display = "none";
    }
}


async function displayReviews() {
    const apiKey = localStorage.getItem("api_key");
    const response = await fetch("/get-snippets/", {
        method: "GET",
        headers: { "api_key": apiKey }
    });

    if (response.ok) {
        const data = await response.json();
        const reviews = data.snippets;
        const carousel = document.getElementById("review-carousel");
        carousel.innerHTML = ''; 

        reviews.forEach(review => {
            const reviewElement = document.createElement("div");
            reviewElement.classList.add("review");
            reviewElement.innerHTML = `<p>${review.embed_code}</p>`;
            carousel.appendChild(reviewElement);
        });
    } else {
        console.error("Failed to fetch reviews.");
    }
}
