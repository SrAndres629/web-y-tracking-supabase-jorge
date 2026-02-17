/**
 * 🚀 SLIDER MANAGER ENHANCED - Mobile-First Implementation
 * Before/After Slider with Hammer.js for touch gestures
 * Addresses: Touch targets < 44px, swipe not working on mobile
 */

import { Logger } from '../core/logger.js';

const DEBUG = new URLSearchParams(window.location.search).has('debug_slider');

export class SliderManagerEnhanced {
    constructor() {
        this.sliders = [];
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }

    init() {
        if (DEBUG) Logger.debug('[SliderEnhanced] Initializing...');
        
        // Load Hammer.js dynamically if needed
        this.loadHammerJS().then(() => {
            this.findSliders();
            this.setupSliders();
        });

        // Handle resize
        window.addEventListener('resize', this.debounce(() => {
            this.sliders.forEach(slider => this.updateSliderDimensions(slider));
        }, 250));
    }

    async loadHammerJS() {
        if (window.Hammer) return Promise.resolve();
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js';
            script.async = true;
            script.onload = () => {
                if (DEBUG) Logger.debug('[SliderEnhanced] Hammer.js loaded');
                resolve();
            };
            script.onerror = () => {
                console.warn('[SliderEnhanced] Failed to load Hammer.js, using fallback');
                resolve(); // Continue without Hammer
            };
            document.head.appendChild(script);
        });
    }

    findSliders() {
        const containers = document.querySelectorAll('.ba-slider, .before-after-slider, [data-slider]');
        
        containers.forEach((container, index) => {
            const slider = {
                id: `slider-${index}`,
                container: container,
                handle: container.querySelector('.slider-handle, .ba-handle'),
                before: container.querySelector('.before, .ba-before'),
                after: container.querySelector('.after, .ba-after'),
                isDragging: false,
                position: 50 // Default 50%
            };
            
            if (slider.before && slider.after) {
                this.sliders.push(slider);
            }
        });

        if (DEBUG) Logger.debug(`[SliderEnhanced] Found ${this.sliders.length} sliders`);
    }

    setupSliders() {
        this.sliders.forEach(slider => {
            this.setupSlider(slider);
            this.updateSliderDimensions(slider);
            
            // Initial position
            this.setSliderPosition(slider, 50);
        });
    }

    setupSlider(slider) {
        const { container, handle } = slider;
        
        // Make handle larger for touch (44px min)
        if (handle) {
            handle.style.minWidth = '44px';
            handle.style.minHeight = '44px';
            handle.style.touchAction = 'none'; // Prevent scroll while dragging
        }

        // Touch/Mouse events
        if (window.Hammer) {
            this.setupHammerGestures(slider);
        } else {
            this.setupNativeGestures(slider);
        }

        // Click to jump
        container.addEventListener('click', (e) => {
            if (e.target === handle || handle?.contains(e.target)) return;
            
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percentage = (x / rect.width) * 100;
            
            this.animateSliderTo(slider, percentage);
        });
    }

    setupHammerGestures(slider) {
        const { container, handle } = slider;
        const element = handle || container;
        
        const mc = new Hammer.Manager(element);
        mc.add(new Hammer.Pan({ direction: Hammer.DIRECTION_HORIZONTAL, threshold: 0 }));
        
        mc.on('panstart', () => {
            slider.isDragging = true;
            container.classList.add('is-dragging');
            if (DEBUG) Logger.debug('[SliderEnhanced] Pan start');
        });
        
        mc.on('panmove', (e) => {
            if (!slider.isDragging) return;
            
            const rect = container.getBoundingClientRect();
            const x = e.center.x - rect.left;
            let percentage = (x / rect.width) * 100;
            
            // Clamp between 0 and 100
            percentage = Math.max(0, Math.min(100, percentage));
            
            this.setSliderPosition(slider, percentage);
        });
        
        mc.on('panend', () => {
            slider.isDragging = false;
            container.classList.remove('is-dragging');
            if (DEBUG) Logger.debug('[SliderEnhanced] Pan end');
        });
    }

    setupNativeGestures(slider) {
        const { container, handle } = slider;
        const element = handle || container;
        
        // Mouse events
        element.addEventListener('mousedown', (e) => this.startDrag(e, slider));
        document.addEventListener('mousemove', (e) => this.onDrag(e, slider));
        document.addEventListener('mouseup', () => this.endDrag(slider));
        
        // Touch events
        element.addEventListener('touchstart', (e) => {
            e.preventDefault(); // Prevent scroll
            this.startDrag(e.touches[0], slider);
        }, { passive: false });
        
        document.addEventListener('touchmove', (e) => {
            if (slider.isDragging) {
                e.preventDefault(); // Prevent scroll while dragging
                this.onDrag(e.touches[0], slider);
            }
        }, { passive: false });
        
        document.addEventListener('touchend', () => this.endDrag(slider));
    }

    startDrag(e, slider) {
        slider.isDragging = true;
        slider.container.classList.add('is-dragging');
        slider.startX = e.clientX;
        slider.startPosition = slider.position;
    }

    onDrag(e, slider) {
        if (!slider.isDragging) return;
        
        const rect = slider.container.getBoundingClientRect();
        const deltaX = e.clientX - slider.startX;
        const deltaPercent = (deltaX / rect.width) * 100;
        
        let newPosition = slider.startPosition + deltaPercent;
        newPosition = Math.max(0, Math.min(100, newPosition));
        
        this.setSliderPosition(slider, newPosition);
    }

    endDrag(slider) {
        slider.isDragging = false;
        slider.container.classList.remove('is-dragging');
    }

    setSliderPosition(slider, percentage) {
        slider.position = percentage;
        
        const { before, after, handle } = slider;
        
        if (before) {
            before.style.clipPath = `inset(0 ${100 - percentage}% 0 0)`;
        }
        
        if (after) {
            after.style.clipPath = `inset(0 0 0 ${percentage}%)`;
        }
        
        if (handle) {
            handle.style.left = `${percentage}%`;
            handle.style.transform = 'translateX(-50%)';
        }
        
        // Update ARIA
        slider.container.setAttribute('aria-valuenow', Math.round(percentage));
    }

    animateSliderTo(slider, targetPercentage) {
        const startPercentage = slider.position;
        const diff = targetPercentage - startPercentage;
        const duration = 300; // ms
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentPercentage = startPercentage + (diff * easeProgress);
            
            this.setSliderPosition(slider, currentPercentage);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    updateSliderDimensions(slider) {
        // Recalculate on resize if needed
        const rect = slider.container.getBoundingClientRect();
        slider.width = rect.width;
        slider.height = rect.height;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Public API
    refresh() {
        this.sliders = [];
        this.findSliders();
        this.setupSliders();
    }

    destroy() {
        this.sliders = [];
    }
}

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const manager = new SliderManagerEnhanced();
        manager.init();
        window.SliderManagerEnhanced = manager;
    });
} else {
    const manager = new SliderManagerEnhanced();
    manager.init();
    window.SliderManagerEnhanced = manager;
}

export default SliderManagerEnhanced;
