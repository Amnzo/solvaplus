class ProSlider {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.navBtns = document.querySelectorAll('.nav-btn');
        this.currentSlide = 0;
        this.autoPlayInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startAutoPlay();
    }

    setupEventListeners() {
        // Navigation buttons
        this.navBtns.forEach((btn, index) => {
            btn.addEventListener('click', () => this.goToSlide(index));
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') this.nextSlide();
            if (e.key === 'ArrowLeft') this.prevSlide();
        });

        // Mouse wheel navigation
        this.slides[0].addEventListener('wheel', (e) => {
            if (e.deltaY > 0) this.nextSlide();
            else this.prevSlide();
        });
    }

    goToSlide(index) {
        // Remove active class from current slide
        this.slides[this.currentSlide].classList.remove('active');
        this.navBtns[this.currentSlide].classList.remove('active');

        // Update current slide
        this.currentSlide = index;

        // Add active class to new slide
        this.slides[this.currentSlide].classList.add('active');
        this.navBtns[this.currentSlide].classList.add('active');

        // Reset auto-play
        this.startAutoPlay();
    }

    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }

    prevSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }

    startAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
        }
        this.autoPlayInterval = setInterval(() => this.nextSlide(), 5000);
    }
}

// Initialize the slider when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ProSlider();
});

// Add smooth scroll animation for navigation
$(document).ready(function() {
    // Smooth scroll for navigation links
    $('.nav-link').on('click', function(e) {
        e.preventDefault();
        const target = $($(this).attr('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 60 // Adjust for fixed navbar
            }, 1000, 'easeInOutExpo');
        }
    });

    // Add parallax effect to sections
    $(window).scroll(function() {
        $('.modern-slider').css('transform', 'translateY(' + $(window).scrollTop() / 2 + 'px)');
    });
});
