class WidgetEditor {
    constructor(container) {
        this.container = container;
        this.businessId = '';  // Will be set when initialized
        this.settings = {
            theme: 'light',
            fontFamily: 'Inter, sans-serif',
            textColor: '#1e293b',
            starColor: '#eab308',
            backgroundColor: '#ffffff',
            cardBackground: '#f8fafc',
            textSize: 14,
            reviewsPerRow: 2,
            containerWidth: '100%',
            borderRadius: 8,
            spacing: 16
        };
        
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
        this.updatePreview();
    }

    render() {
        this.container.innerHTML = `
            <div class="widget-editor">
                <div class="widget-editor-tabs">
                    <div class="widget-editor-tab active" data-tab="appearance">Appearance</div>
                    <div class="widget-editor-tab" data-tab="layout">Layout</div>
                    <div class="widget-editor-tab" data-tab="embed">Embed Code</div>
                </div>
                
                <div class="widget-editor-content">
                    <div class="widget-editor-panel active" data-panel="appearance">
                        <div class="control-group">
                            <label class="control-label">Theme</label>
                            <select class="theme-select">
                                <option value="light">Light</option>
                                <option value="dark">Dark</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Font Family</label>
                            <select class="font-select">
                                <option value="Inter, sans-serif">Inter</option>
                                <option value="'SF Pro Display', sans-serif">SF Pro</option>
                                <option value="'Roboto', sans-serif">Roboto</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Text Color</label>
                            <div class="color-control">
                                <div class="color-wheel">
                                    <input type="color" class="text-color" value="${this.settings.textColor}">
                                </div>
                                <input type="text" class="color-value text-color-value" value="${this.settings.textColor}">
                            </div>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Star Color</label>
                            <div class="color-control">
                                <div class="color-wheel">
                                    <input type="color" class="star-color" value="${this.settings.starColor}">
                                </div>
                                <input type="text" class="color-value star-color-value" value="${this.settings.starColor}">
                            </div>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Text Size</label>
                            <div class="range-control">
                                <input type="range" class="range-slider text-size" min="12" max="20" value="${this.settings.textSize}">
                                <input type="number" class="range-value text-size-value" value="${this.settings.textSize}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="widget-editor-panel" data-panel="layout">
                        <div class="control-group">
                            <label class="control-label">Reviews Per Row</label>
                            <select class="reviews-per-row">
                                <option value="1">1</option>
                                <option value="2" selected>2</option>
                                <option value="3">3</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Container Width</label>
                            <select class="container-width">
                                <option value="100%">Full Width</option>
                                <option value="800px">800px</option>
                                <option value="1000px">1000px</option>
                            </select>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Border Radius</label>
                            <div class="range-control">
                                <input type="range" class="range-slider border-radius" min="0" max="20" value="${this.settings.borderRadius}">
                                <input type="number" class="range-value border-radius-value" value="${this.settings.borderRadius}">
                            </div>
                        </div>
                        
                        <div class="control-group">
                            <label class="control-label">Spacing</label>
                            <div class="range-control">
                                <input type="range" class="range-slider spacing" min="8" max="32" value="${this.settings.spacing}">
                                <input type="number" class="range-value spacing-value" value="${this.settings.spacing}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="widget-editor-panel" data-panel="embed">
                        <div class="embed-code">
                            <textarea readonly></textarea>
                            <button class="copy-button">Copy Code</button>
                        </div>
                    </div>
                    
                    <div class="preview-container">
                        <div id="widget-preview"></div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Tab switching
        this.container.querySelectorAll('.widget-editor-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // Color inputs
        this.container.querySelectorAll('input[type="color"]').forEach(input => {
            input.addEventListener('input', (e) => {
                const valueInput = this.container.querySelector(`.${input.className}-value`);
                valueInput.value = e.target.value;
                this.updateSettings();
            });
        });

        // Color value inputs
        this.container.querySelectorAll('.color-value').forEach(input => {
            input.addEventListener('input', (e) => {
                const colorInput = this.container.querySelector(`.${input.className.replace('-value', '')}`);
                colorInput.value = e.target.value;
                this.updateSettings();
            });
        });

        // Range inputs
        this.container.querySelectorAll('.range-slider').forEach(input => {
            input.addEventListener('input', (e) => {
                const valueInput = this.container.querySelector(`.${input.className.replace('range-slider', 'range-value')}`);
                valueInput.value = e.target.value;
                this.updateSettings();
            });
        });

        // Select inputs
        this.container.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => this.updateSettings());
        });

        // Copy button
        this.container.querySelector('.copy-button').addEventListener('click', () => this.copyEmbedCode());
    }

    switchTab(tabName) {
        this.container.querySelectorAll('.widget-editor-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        this.container.querySelectorAll('.widget-editor-panel').forEach(panel => {
            panel.classList.toggle('active', panel.dataset.panel === tabName);
        });
    }

    updateSettings() {
        // Update settings object based on current input values
        this.settings = {
            theme: this.container.querySelector('.theme-select').value,
            fontFamily: this.container.querySelector('.font-select').value,
            textColor: this.container.querySelector('.text-color').value,
            starColor: this.container.querySelector('.star-color').value,
            textSize: parseInt(this.container.querySelector('.text-size').value),
            reviewsPerRow: parseInt(this.container.querySelector('.reviews-per-row').value),
            containerWidth: this.container.querySelector('.container-width').value,
            borderRadius: parseInt(this.container.querySelector('.border-radius').value),
            spacing: parseInt(this.container.querySelector('.spacing').value)
        };

        this.updatePreview();
        this.updateEmbedCode();
    }

    updatePreview() {
        // Update the main widget with new settings
        BusinessReviewsWidget.init(this.settings);
    }

    updateEmbedCode() {
        const embedCode = `
<div id="business-reviews-widget" data-business-id="${this.businessId}"></div>
<script src="${window.location.origin}/static/widget.js"></script>
<script>
    BusinessReviewsWidget.init(${JSON.stringify(this.settings, null, 2)});
</script>`;
        
        this.container.querySelector('.embed-code textarea').value = embedCode.trim();
    }

    copyEmbedCode() {
        const textarea = this.container.querySelector('.embed-code textarea');
        textarea.select();
        document.execCommand('copy');
        
        const button = this.container.querySelector('.copy-button');
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => button.textContent = originalText, 2000);
    }
} 