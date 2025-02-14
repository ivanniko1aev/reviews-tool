class BusinessReviewsWidget {
    static init(settings) {
        const container = document.getElementById('business-reviews-widget');
        if (!container) {
            console.error('Widget container not found');
            return;
        }
        
        const businessId = container.dataset.businessId;
        if (!businessId) {
            container.innerHTML = '<p class="text-gray-500">No business selected</p>';
            return;
        }
        
        this.applyStyles(settings);
        this.loadReviews(businessId);
    }

    static applyStyles(settings) {
        const styleId = 'business-reviews-widget-styles';
        let styleEl = document.getElementById(styleId);
        
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = styleId;
            document.head.appendChild(styleEl);
        }

        styleEl.textContent = `
            #business-reviews-widget {
                width: ${settings.containerWidth};
                margin: 0 auto;
                font-family: ${settings.fontFamily};
            }
            
            .widget-reviews-grid {
                display: grid;
                grid-template-columns: repeat(${settings.reviewsPerRow}, 1fr);
                gap: ${settings.spacing}px;
                color: ${settings.textColor};
                font-size: ${settings.textSize}px;
            }
            
            .widget-review-card {
                background: ${settings.cardBackground};
                padding: ${settings.spacing}px;
                border-radius: ${settings.borderRadius}px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .widget-stars {
                color: ${settings.starColor};
            }
            
            .widget-author-image {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                object-fit: cover;
            }
            
            .widget-review-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }
            
            .widget-review-meta {
                flex: 1;
            }
            
            .widget-review-content {
                line-height: 1.5;
            }
            
            .widget-review-date {
                margin-top: 8px;
                font-size: 0.875em;
                opacity: 0.7;
            }
        `;
    }

    static loadReviews(businessId) {
        fetch(`/api/reviews/${businessId}`)
            .then(response => response.json())
            .then(data => {
                console.log('Review data:', data.reviews);
                this.renderReviews(data.reviews);
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
                const container = document.getElementById('business-reviews-widget');
                if (container) {
                    container.innerHTML = '<p class="text-red-500 text-center">Error loading reviews. Please try again later.</p>';
                }
            });
    }

    static renderReviews(reviews) {
        const container = document.getElementById('business-reviews-widget');
        if (!container) {
            console.error('Widget container not found');
            return;
        }

        if (!reviews || reviews.length === 0) {
            container.innerHTML = '<p>No reviews to display</p>';
            return;
        }

        const formatDate = (dateStr) => {
            if (!dateStr) return '';
            const date = new Date(dateStr);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) return 'Today';
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
            if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
            return `${Math.floor(diffDays / 365)} years ago`;
        };

        const reviewsHTML = reviews.map(review => `
            <div class="widget-review-card">
                <div class="widget-review-header">
                    <img src="${review.profile_photo_url || '/static/default-avatar.png'}" 
                         alt="${review.author}" 
                         class="widget-author-image">
                    <div class="widget-review-meta">
                        <div class="widget-author-name">${review.author}</div>
                        <div class="widget-stars">
                            ${'★'.repeat(parseInt(review.rating))}${'☆'.repeat(5-parseInt(review.rating))}
                        </div>
                    </div>
                </div>
                <div class="widget-review-content">${review.content}</div>
                <div class="widget-review-date">${formatDate(review.date)}</div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="widget-reviews-grid">
                ${reviewsHTML}
            </div>
        `;
    }
} 