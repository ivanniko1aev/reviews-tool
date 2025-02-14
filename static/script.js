console.log('script.js loaded'); // Debug line

// Handle login button click - Show the signup modal
document.getElementById("login-btn").addEventListener("click", () => {
    document.getElementById("signup-modal").classList.remove("hidden");
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
            document.getElementById("signup-modal").classList.add("hidden");
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
        document.getElementById("login-btn").classList.add("hidden");
        document.getElementById("logout-btn").classList.remove("hidden");
    } else {
        document.getElementById("login-btn").classList.remove("hidden");
        document.getElementById("logout-btn").classList.add("hidden");
    }
}
/*
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
            reviewElement.classList.add("review", "bg-gray-100", "p-4", "rounded-lg", "shadow-md");
            reviewElement.innerHTML = `<p class="text-center">${review.embed_code}</p>`;
            carousel.appendChild(reviewElement);
        });
    } else {
        console.error("Failed to fetch reviews.");
    }
}

const defaultUrl = "https://maps.googleapis.com/maps/api/place/autocomplete/json";

async function placeAutocomplete(input) {
    const apiKey = 'GOOGLE_MAPS_API_KEY'; // Replace with your actual API key
    const params = {
        input: input,
        key: apiKey,
        // Add other parameters as needed
    };

    try {
        const response = await axios.get(defaultUrl, { params });
        return response.data.predictions; // Return the predictions
    } catch (error) {
        console.error('Error fetching autocomplete suggestions:', error);
        return [];
    }
}

let autocomplete;

function initAutocomplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'), // Ensure this matches the input ID
        {
            types: ['establishment'], // Specify the types of places to return
            componentRestrictions: { country: ['AU'] }, // Restrict to Australia
            fields: ['place_id', 'geometry', 'name'] // Specify the fields to return
        }
    );

    // Set up the listener for when the user selects a place
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (place && place.place_id) {
            console.log('Selected Place ID:', place.place_id);
            console.log('Selected Place Name:', place.name);
            // You can trigger your review scraping logic here
        } else {
            console.warn('No place selected or place ID not available.');
        }
    });
}

// Ensure the initAutocomplete function is called when the API is loaded
window.initAutocomplete = initAutocomplete;
*/
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Loading dashboard...'); // Debug line
    
    try {
        const response = await fetch('/api/saved-business', {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            if (data.business) {
                // If there's a saved business, display it
                selectPlace({
                    id: data.business.place_id,
                    displayName: { text: data.business.business_name },
                    formattedAddress: data.business.business_address || ''
                });
            }
            // If no saved business, do nothing (search form is already visible)
        }
    } catch (error) {
        console.error('Error checking for saved business:', error);
    }
});

function displayResults(places) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results

    if (places && places.length > 0) {
        places.forEach(place => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item p-4 border rounded-md mb-2 cursor-pointer hover:bg-gray-100 transition-colors';
            resultItem.innerHTML = `
                <div class="font-bold">${place.displayName.text}</div>
                <div class="text-sm text-gray-600">${place.formattedAddress}</div>
            `;
            resultItem.onclick = () => selectPlace(place);
            resultsContainer.appendChild(resultItem);
        });
    } else {
        resultsContainer.innerHTML = '<p class="text-center text-gray-600">No results found.</p>';
    }
}

async function selectPlace(place) {
    console.log('Selecting place:', place); // Debug log
    
    // Show the selected business section
    const selectedSection = document.getElementById('selected-business-section');
    selectedSection.classList.remove('hidden');

    // Update the selected business info
    document.getElementById('selected-business-name').textContent = place.displayName.text;
    document.getElementById('selected-business-address').textContent = place.formattedAddress;

    // Save the business selection
    try {
        const response = await fetch('/api/save-business', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                place_id: place.id,
                business_name: place.displayName.text,
                business_address: place.formattedAddress
            }),
            // Include credentials to send cookies
            credentials: 'include'
        });

        console.log('Save business response status:', response.status); // Debug log

        if (!response.ok) {
            console.error('Failed to save business selection');
        } else {
            const result = await response.json();
            console.log('Save business result:', result);
        }
    } catch (error) {
        console.error('Error saving business selection:', error);
    }

    // Fetch reviews for the selected place
    console.log('Fetching reviews for place ID:', place.id);
    fetchReviews(place.id);
}

async function fetchReviews(placeId) {
    try {
        // Show loading state
        document.getElementById('loading-reviews').classList.remove('hidden');
        document.getElementById('reviews-container').innerHTML = ''; // Clear existing content

        const response = await fetch(`/api/reviews/${placeId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received reviews data:', data); // Debug log

        if (!data.reviews || !Array.isArray(data.reviews)) {
            throw new Error('Invalid reviews data format');
        }

        displayReviews(data.reviews);
    } catch (error) {
        console.error('Error fetching reviews:', error);
        document.getElementById('reviews-container').innerHTML = 
            '<p class="text-red-500 text-center">Error loading reviews. Please try again later.</p>';
    } finally {
        document.getElementById('loading-reviews').classList.add('hidden');
    }
}

function displayReviews(reviews) {
    const container = document.getElementById('reviews-container');
    container.innerHTML = '';

    if (!reviews || reviews.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-600">No reviews found for this business.</p>';
        return;
    }

    reviews.forEach(review => {
        const reviewElement = document.createElement('div');
        reviewElement.className = 'review-card bg-white p-4 rounded-lg shadow-md mb-4';
        
        const fallbackAvatar = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(review.author);
        const img = new Image();
        let retryCount = 0;
        const maxRetries = 2;  // Maximum number of retries

        img.onload = () => {
            // Image loaded successfully
            img.className = 'w-10 h-10 rounded-full mr-2';
        };

        img.onerror = () => {
            if (retryCount < maxRetries && review.profile_photo_url) {
                // Retry loading the original image
                retryCount++;
                img.src = review.profile_photo_url;
            } else {
                // After max retries or if no profile photo URL, use fallback
                img.src = fallbackAvatar;
            }
        };

        // Initial load attempt
        img.src = review.profile_photo_url || fallbackAvatar;
        
        reviewElement.innerHTML = `
            <div class="flex items-center mb-2">
                <div class="avatar-container">
                    ${img.outerHTML}
                </div>
                <div>
                    <div class="font-semibold">${review.author}</div>
                    <div class="text-yellow-400">
                        ${'★'.repeat(review.rating)}${'☆'.repeat(5-review.rating)}
                    </div>
                </div>
            </div>
            <p class="text-gray-600 mt-2">${review.content}</p>
            <div class="text-sm text-gray-400 mt-2">${review.relative_time}</div>
        `;
        
        container.appendChild(reviewElement);
    });

    // Also update the reviews preview if the customization panel is open
    if (!document.getElementById('customization-panel').classList.contains('hidden')) {
        updatePreview();
    }
}

let currentReviews = []; // Store the current reviews

function toggleCustomizer() {
    const panel = document.getElementById('customization-panel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        updatePreview();
    }
}

function updatePreview() {
    const settings = getCustomizationSettings();
    const previewContainer = document.getElementById('reviews-preview');
    
    // Apply styles to preview container
    previewContainer.style.fontFamily = settings.fontFamily;
    previewContainer.style.color = settings.textColor;
    previewContainer.style.width = settings.containerWidth;
    
    // Generate preview HTML
    const previewHTML = generateReviewsHTML(currentReviews, settings);
    previewContainer.innerHTML = previewHTML;
    
    // Update embed code
    generateEmbedCode(settings);
}

function getCustomizationSettings() {
    return {
        fontFamily: document.getElementById('font-family').value,
        textColor: document.getElementById('text-color').value,
        starColor: document.getElementById('star-color').value,
        textSize: document.getElementById('text-size').value + 'px',
        containerWidth: document.getElementById('container-width').value,
        reviewsPerRow: document.getElementById('reviews-per-row').value
    };
}

function generateReviewsHTML(reviews, settings) {
    if (!reviews || reviews.length === 0) return '<p>No reviews to display</p>';

    const gridCols = `grid-template-columns: repeat(${settings.reviewsPerRow}, 1fr);`;
    
    return `
        <style>
            .custom-reviews-grid {
                display: grid;
                ${gridCols}
                gap: 1rem;
            }
            .custom-review-card {
                font-family: ${settings.fontFamily};
                color: ${settings.textColor};
                font-size: ${settings.textSize};
                background: white;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .custom-stars {
                color: ${settings.starColor};
            }
        </style>
        <div class="custom-reviews-grid">
            ${reviews.map(review => `
                <div class="custom-review-card">
                    <div class="flex items-center mb-2">
                        <img src="${review.profile_photo_url || '/static/default-avatar.png'}" 
                             alt="${review.author}" 
                             class="w-10 h-10 rounded-full mr-2">
                        <div>
                            <div class="font-semibold">${review.author}</div>
                            <div class="custom-stars">
                                ${'★'.repeat(parseInt(review.rating))}${'☆'.repeat(5-parseInt(review.rating))}
                            </div>
                        </div>
                    </div>
                    <p class="mt-2">${review.content}</p>
                    <div class="text-sm opacity-75 mt-2">${review.relative_time}</div>
                </div>
            `).join('')}
        </div>
    `;
}

async function generateEmbedCode(settings) {
    const currentPlace = document.getElementById('selected-business-name').textContent;
    const embedCode = `
<div id="business-reviews-widget" 
     data-business-id="${currentBusinessId}"
     style="width: ${settings.containerWidth}; font-family: ${settings.fontFamily};">
    <script src="${window.location.origin}/static/widget.js"></script>
    <script>
        BusinessReviewsWidget.init({
            fontFamily: '${settings.fontFamily}',
            textColor: '${settings.textColor}',
            starColor: '${settings.starColor}',
            textSize: '${settings.textSize}',
            reviewsPerRow: ${settings.reviewsPerRow}
        });
    </script>
</div>`;

    document.getElementById('embed-code').value = embedCode;

    // Save the settings to the database
    try {
        const response = await fetch('/api/save-embed', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...settings,
                embedCode,
                businessUrl: currentBusinessId
            }),
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Failed to save embed settings');
        }
    } catch (error) {
        console.error('Error saving embed settings:', error);
    }
}

function copyEmbedCode() {
    const embedCode = document.getElementById('embed-code');
    embedCode.select();
    document.execCommand('copy');
    
    // Show feedback
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}

function handleSearchClick() {
    const businessName = document.getElementById('business_name').value;

    if (!businessName) {
        alert('Please enter a business name.');
        return;
    }

    // Show loading state in results container
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p class="mt-2">Searching...</p>
        </div>
    `;

    // Hide the selected business section if it was previously shown
    document.getElementById('selected-business-section').classList.add('hidden');

    fetch('/api/places', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ textQuery: businessName })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received data:', data);
        
        resultsContainer.innerHTML = '';

        // Check if we have places in the response
        if (data && data.places && data.places.length > 0) {
            // Create a result item for each place
            data.places.forEach(place => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item p-4 border rounded-md mb-2 cursor-pointer hover:bg-gray-100 transition-colors';
                resultItem.innerHTML = `
                    <div class="font-bold">${place.displayName.text}</div>
                    <div class="text-sm text-gray-600">${place.formattedAddress}</div>
                `;
                resultItem.onclick = () => {
                    console.log('Selected:', place);
                    selectPlace(place);
                };
                resultsContainer.appendChild(resultItem);
            });
        } else {
            resultsContainer.innerHTML = '<p class="text-center text-gray-600">No results found</p>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultsContainer.innerHTML = '<p class="text-red-500 text-center">Error fetching results. Please try again.</p>';
    });
}

// Add function to load saved business on page load
async function loadSavedBusiness() {
    console.log('loadSavedBusiness called'); // Debug line
    try {
        console.log('Attempting to load saved business...'); // Debug line
        const response = await fetch('/api/saved-business', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        console.log('Load business response status:', response.status); // Debug line

        if (response.ok) {
            const data = await response.json();
            console.log('Loaded saved business data:', data); // Debug line
            if (data.business) {
                // Simulate selecting the place
                selectPlace({
                    id: data.business.place_id,
                    displayName: { text: data.business.business_name },
                    formattedAddress: data.business.business_address
                });
            } else {
                console.log('No saved business found'); // Debug line
            }
        } else {
            console.error('Failed to load saved business, status:', response.status);
        }
    } catch (error) {
        console.error('Error loading saved business:', error);
        throw error; // Re-throw to be caught by the caller
    }
}