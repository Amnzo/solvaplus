// Slider automatique
class ProductSlider {
    constructor() {
        this.currentSlide = 0;
        this.slides = document.querySelectorAll('.slider-item');
        this.controls = document.querySelectorAll('.slider-control');
        this.slider = document.querySelector('.slider');
        this.totalSlides = this.slides.length;
        this.setupControls();
        this.startAutoSlide();
    }

    setupControls() {
        this.controls.forEach((control, index) => {
            control.addEventListener('click', () => this.goToSlide(index));
        });
    }

    goToSlide(index) {
        this.currentSlide = index;
        this.updateSlider();
    }

    updateSlider() {
        // Mettre à jour la position du slider
        this.slider.style.transform = `translateX(-${this.currentSlide * 100}%)`;
        
        // Mettre à jour les contrôles
        this.controls.forEach((control, index) => {
            control.classList.toggle('active', index === this.currentSlide);
        });
        
        // Mettre à jour les classes actives des slides
        this.slides.forEach((slide, index) => {
            slide.classList.toggle('active', index === this.currentSlide);
        });
    }

    startAutoSlide() {
        setInterval(() => {
            this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
            this.updateSlider();
        }, 8000); // Changer de slide toutes les 8 secondes
    }
}

// Initialiser le slider
document.addEventListener('DOMContentLoaded', () => {
    new ProductSlider();
});
