// Slider amélioré avec flèches de navigation
class EnhancedSlider {
    constructor() {
        try {
            this.currentSlide = 0;
            this.slides = document.querySelectorAll('.slider-item');
            this.controls = document.querySelectorAll('.slider-control');
            this.slider = document.querySelector('.slider');
            this.totalSlides = this.slides.length;
            this.setupControls();
            this.setupNavigation();
            this.updateSlider(); // Initialiser la première slide
            this.startAutoSlide();
            console.log('Slider initialisé avec', this.totalSlides, 'slides');
        } catch (error) {
            console.error('Erreur lors de l\'initialisation du slider:', error);
        }
    }

    setupControls() {
        try {
            this.controls.forEach((control, index) => {
                control.addEventListener('click', () => this.goToSlide(index));
            });
        } catch (error) {
            console.error('Erreur lors du setup des contrôles:', error);
        }
    }

    setupNavigation() {
        try {
            const prevBtn = document.querySelector('.slider-nav.prev');
            const nextBtn = document.querySelector('.slider-nav.next');
            
            if (prevBtn && nextBtn) {
                prevBtn.addEventListener('click', () => this.goToPrevSlide());
                nextBtn.addEventListener('click', () => this.goToNextSlide());
            }
        } catch (error) {
            console.error('Erreur lors du setup de la navigation:', error);
        }
    }

    goToSlide(index) {
        try {
            this.currentSlide = index;
            this.updateSlider();
        } catch (error) {
            console.error('Erreur lors du changement de slide:', error);
        }
    }

    goToPrevSlide() {
        this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.updateSlider();
    }

    goToNextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.updateSlider();
    }

    updateSlider() {
        try {
            // Désactiver l'auto-slide pendant la transition
            this.stopAutoSlide();
            
            // Mettre à jour la position du slider
            this.slider.style.transform = `translateX(-${this.currentSlide * 100}%)`;
            
            // Mettre à jour les contrôles
            this.controls.forEach((control, index) => {
                control.classList.remove('active');
                if (index === this.currentSlide) {
                    control.classList.add('active');
                }
            });
            
            // Mettre à jour les classes actives des slides
            this.slides.forEach((slide, index) => {
                slide.classList.remove('active');
                if (index === this.currentSlide) {
                    slide.classList.add('active');
                }
            });
            
            // Réactiver l'auto-slide après une courte pause
            setTimeout(() => {
                this.startAutoSlide();
            }, 1000);
        } catch (error) {
            console.error('Erreur lors de la mise à jour du slider:', error);
        }
    }

    startAutoSlide() {
        try {
            // Augmenter le temps entre les slides
            this.interval = setInterval(() => {
                this.goToNextSlide();
            }, 5000); // Changer de slide toutes les 5 secondes
            console.log('Auto-slide démarré');
        } catch (error) {
            console.error('Erreur lors du démarrage de l\'auto-slide:', error);
        }
    }

    stopAutoSlide() {
        try {
            clearInterval(this.interval);
            console.log('Auto-slide arrêté');
        } catch (error) {
            console.error('Erreur lors de l\'arrêt de l\'auto-slide:', error);
        }
    }
}

// Initialiser le slider
document.addEventListener('DOMContentLoaded', () => {
    const slider = new EnhancedSlider();
    
    // Arrêter l'auto-slide pendant l'interaction
    document.querySelector('.slider-container').addEventListener('mouseenter', () => {
        slider.stopAutoSlide();
    });
    
    document.querySelector('.slider-container').addEventListener('mouseleave', () => {
        slider.startAutoSlide();
    });
});
