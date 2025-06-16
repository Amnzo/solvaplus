// Chat en direct
$(document).ready(function() {
    // Animation du chat
    $('.chat-button').click(function() {
        $('.chat-box').slideToggle('fast');
        $(this).toggleClass('active');
    });

    // Fermer le chat quand on clique en dehors
    $(document).click(function(e) {
        if (!$(e.target).closest('.chat-widget').length && $('.chat-box').is(':visible')) {
            $('.chat-box').slideUp('fast');
            $('.chat-button').removeClass('active');
        }
    });

    // Gestion des messages
    $('.chat-box .btn-primary').click(function() {
        var message = $('.chat-box input').val();
        if (message.trim() !== '') {
            addMessage('user', message);
            $('.chat-box input').val('');
            // Simuler une réponse
            setTimeout(function() {
                addMessage('bot', 'Merci pour votre message ! Un conseiller va vous répondre sous peu.');
            }, 1000);
        }
    });

    // Animation des cartes de contact
    $('.contact-card, .contact-info-item').hover(function() {
        $(this).addClass('animate__animated animate__bounce');
    }, function() {
        $(this).removeClass('animate__animated animate__bounce');
    });
});

// Fonction pour ajouter un message
function addMessage(sender, message) {
    var messageDiv = $('<div class="message ' + sender + '">' + message + '</div>');
    $('.chat-messages').append(messageDiv);
    $('.chat-messages').scrollTop($('.chat-messages')[0].scrollHeight);
}
