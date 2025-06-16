// Effets de slide dynamiques
$(document).ready(function() {
    // Effet de révélation pour les cartes de catégories
    $('.category-card').each(function(index) {
        $(this).addClass('category-card').delay(index * 300).queue(function() {
            $(this).addClass('animate-on-load');
        });
    });

    // Effet de slide pour les cartes de contact
    $('.contact-info-item').each(function(index) {
        $(this).addClass('flash-slide-up').delay(index * 200).queue(function() {
            $(this).addClass('flash-float');
        });
    });

    // Effet de slide pour le formulaire
    $('.contact-form').addClass('flash-slide-in');

    // Effet de scale pour les titres
    $('h2, h3, h4').addClass('flash-scale');

    // Effet de tada pour les icônes importantes
    $('.fa-headset, .fa-comments').addClass('flash-tada');

    // Effet de vague pour les liens
    $('.nav-link').hover(
        function() {
            $(this).addClass('flash-wave');
        },
        function() {
            $(this).removeClass('flash-wave');
        }
    );

    // Effet de float pour les éléments interactifs
    $('.click-ripple').addClass('flash-float');

    // Effet de slide pour le chat
    $('.chat-button').hover(
        function() {
            $(this).addClass('flash-float-right');
        },
        function() {
            $(this).removeClass('flash-float-right');
        }
    );

    // Effet de tada sur les boutons au survol
    $('.btn').hover(
        function() {
            $(this).addClass('flash-tada');
        },
        function() {
            $(this).removeClass('flash-tada');
        }
    );

    // Effet de slide pour les messages de chat
    $('.chat-messages').on('DOMNodeInserted', function(e) {
        $(e.target).addClass('flash-slide-up');
    });

    // Effet de float alterné pour les cartes
    $('.contact-info-item:even').addClass('flash-float-left');
    $('.contact-info-item:odd').addClass('flash-float-right');
});
