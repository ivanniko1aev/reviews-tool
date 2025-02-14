class BusinessReviewsWidget {
    static init(settings) {
        const container = document.getElementById('business-reviews-widget');
        const businessId = container.dataset.businessId;
        
        // Add styles
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .widget-reviews-grid {
                display: grid;
                grid-template-columns: repeat(${settings.reviewsPerRow}, 1fr);
                gap: 1rem;
                font-family: ${settings.fontFamily};
                color: ${settings.textColor};
                font-size: ${settings.textSize};
            }
            .widget-review-card {
                background: white;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .widget-stars {
                color: ${settings.starColor};
            }
        `;
        document.head.appendChild(styleElement);
        
        // Fetch reviews
        fetch(`/api/reviews/${businessId}`)
            .then(response => response.json())
            .then(data => {
                container.innerHTML = this.generateReviewsHTML(data.reviews);
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
                container.innerHTML = '<p>Error loading reviews</p>';
            });
    }

    static generateReviewsHTML(reviews) {
        if (!reviews || reviews.length === 0) return '<p>No reviews to display</p>';
        
        return `
            <div class="widget-reviews-grid">
                ${reviews.map(review => `
                    <div class="widget-review-card">
                        <div class="flex items-center mb-2">
                            <img src="${review.profile_photo_url || '/static/default-avatar.png'}" 
                                 alt="${review.author}" 
                                 class="w-10 h-10 rounded-full mr-2">
                            <div>
                                <div class="font-semibold">${review.author}</div>
                                <div class="widget-stars">
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
} 