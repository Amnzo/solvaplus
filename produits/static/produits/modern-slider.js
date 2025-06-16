class ModernSlider {
    constructor() {
        this.currentSlide = 0;
        this.slides = document.querySelectorAll('.slide');
        this.navBtns = document.querySelectorAll('.nav-btn');
        this.slidesContainer = document.querySelector('.slides');
        this.totalSlides = this.slides.length;
        this.setupNavigation();
        this.startAutoSlide();
    }

    setupNavigation() {
        this.navBtns.forEach((btn, index) => {
            btn.addEventListener('click', () => this.goToSlide(index));
        });
    }

    goToSlide(index) {
        this.currentSlide = index;
        this.updateSlider();
    }

    updateSlider() {
        // Mettre à jour la position des slides
        const translateX = -this.currentSlide * 100 / 3;
        this.slidesContainer.style.transform = `translateX(${translateX}%)`;
        
        // Mettre à jour les points de navigation
        this.navBtns.forEach((btn, index) => {
            btn.classList.toggle('active', index === this.currentSlide);
        });
    }

    startAutoSlide() {
        this.interval = setInterval(() => {
            this.goToNextSlide();
        }, 5000); // Changer de slide toutes les 5 secondes
    }

    goToNextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.updateSlider();
    }
}

// Initialiser le slider quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    new ModernSlider();
});
