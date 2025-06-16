// Slider automatique
let currentSlide = 0;
const slides = document.querySelectorAll('.slider-item');
const totalSlides = slides.length;

function nextSlide() {
    const slider = document.querySelector('.slider');
    currentSlide = (currentSlide + 1) % totalSlides;
    slider.style.transform = `translateX(-${currentSlide * 320}px)`;
}

// Changer de slide toutes les 5 secondes
setInterval(nextSlide, 5000);

// Hover effect sur les cartes
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-10px)';
        card.style.boxShadow = '0 15px 30px rgba(0,0,0,0.2)';
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0)';
        card.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    });
});

// Effet de scroll sur le menu
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(0,0,0,0.9)';
    } else {
        navbar.style.backgroundColor = 'rgba(0,0,0,0.7)';
    }
});

// Animation de chargement
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(element => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.opacity = '1';
        }, 1000);
    });
});
