/* =========================================================
   Brignon-les-Bains — Interactions JS
   Vanilla JS, sans dépendance externe.
   Défensif : chaque bloc vérifie l'existence des éléments
   avant d'attacher des écouteurs, pour fonctionner sur
   toutes les pages sans erreur en console.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

  /* -----------------------------------------------------
     1. Menu mobile (burger)
     ----------------------------------------------------- */
  var navToggle = document.querySelector(".nav-toggle");
  var mainNav = document.querySelector(".main-nav");

  if (navToggle && mainNav) {
    var closeNav = function () {
      mainNav.classList.remove("is-open");
      navToggle.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    };

    var openNav = function () {
      mainNav.classList.add("is-open");
      navToggle.classList.add("is-open");
      navToggle.setAttribute("aria-expanded", "true");
    };

    navToggle.addEventListener("click", function () {
      var isOpen = mainNav.classList.contains("is-open");
      if (isOpen) {
        closeNav();
      } else {
        openNav();
      }
    });

    /* Fermer le menu si on clique sur un lien du menu */
    var navLinks = mainNav.querySelectorAll("a");
    navLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        closeNav();
      });
    });

    /* Fermer le menu avec la touche Échap */
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && mainNav.classList.contains("is-open")) {
        closeNav();
        navToggle.focus();
      }
    });
  }

  /* -----------------------------------------------------
     2. Accordéon des démarches
     ----------------------------------------------------- */
  var accordionHeaders = document.querySelectorAll(".accordion-header");

  if (accordionHeaders.length > 0) {
    accordionHeaders.forEach(function (header) {
      header.addEventListener("click", function () {
        var item = header.closest(".accordion-item");
        if (!item) {
          return;
        }

        var isOpen = item.classList.contains("open");

        if (isOpen) {
          item.classList.remove("open");
          header.setAttribute("aria-expanded", "false");
        } else {
          item.classList.add("open");
          header.setAttribute("aria-expanded", "true");
        }
      });
    });
  }

  /* -----------------------------------------------------
     3. Module de Chat Brigitte (Assistant Municipal)
     ----------------------------------------------------- */
  initMunicipalChat();

  function initMunicipalChat() {
    // 1. Inserer les elements HTML
    var triggerHtml = 
      '<button id="municipal-chat-trigger" aria-label="Ouvrir l\'assistant municipal">' +
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">' +
          '<path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>' +
        '</svg>' +
      '</button>';

    var boxHtml =
      '<div id="municipal-chat-box">' +
        '<div class="chat-header">' +
          '<h3>Brigitte — Aide Municipale</h3>' +
          '<div class="chat-header-actions">' +
            '<button class="chat-reset" aria-label="Nouvelle conversation">↺</button>' +
            '<button class="chat-expand" aria-label="Agrandir le chat">⛶</button>' +
            '<button class="chat-close" aria-label="Fermer le chat">&times;</button>' +
          '</div>' +
        '</div>' +
        '<div class="chat-messages" id="chat-messages-container"></div>' +
        '<div class="chat-suggestions">' +
          '<button class="chat-suggestion-btn" data-text="Quels sont les horaires de la mairie ?">Horaires de la mairie</button>' +
          '<button class="chat-suggestion-btn" data-text="Je veux prendre rendez-vous avec le service urbanisme.">Rdv Urbanisme</button>' +
          '<button class="chat-suggestion-btn" data-text="Je souhaite signaler un lampadaire en panne.">Signaler un incident</button>' +
          '<button class="chat-suggestion-btn" data-text="Je veux réserver une salle municipale.">Réserver une salle</button>' +
          '<button class="chat-suggestion-btn" data-text="Quels documents fournir pour inscrire mon enfant à l\'école ?">Inscription école</button>' +
        '</div>' +
        '<div class="chat-input-area">' +
          '<input type="text" id="chat-input-field" placeholder="Posez votre question ici..." aria-label="Votre question">' +
          '<button id="chat-send-btn">Envoyer</button>' +
        '</div>' +
      '</div>';

    document.body.insertAdjacentHTML('beforeend', triggerHtml);
    document.body.insertAdjacentHTML('beforeend', boxHtml);

    // 2. Variables de session
    var userId = localStorage.getItem('brigitte_user_id') || 'usr_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('brigitte_user_id', userId);
    
    var sessionId = localStorage.getItem('brigitte_session_id') || 'sess_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('brigitte_session_id', sessionId);

    var messagesHistory = JSON.parse(localStorage.getItem('brigitte_history_' + sessionId)) || [];

    // Elements DOM
    var triggerBtn = document.getElementById('municipal-chat-trigger');
    var chatBox = document.getElementById('municipal-chat-box');
    var closeBtn = chatBox.querySelector('.chat-close');
    var expandBtn = chatBox.querySelector('.chat-expand');
    var resetBtn = chatBox.querySelector('.chat-reset');
    var messagesContainer = document.getElementById('chat-messages-container');
    var inputField = document.getElementById('chat-input-field');
    var sendBtn = document.getElementById('chat-send-btn');
    var suggestionBtns = chatBox.querySelectorAll('.chat-suggestion-btn');

    // API URL
    var API_URL = 'http://localhost:8000/run';

    // 3. Charger l'historique
    if (messagesHistory.length === 0) {
      addMessage('assistant', 'Bonjour ! Je suis Brigitte, l\'assistante virtuelle de la mairie de Brignon-les-Bains. Comment puis-je vous aider aujourd\'hui ?', false);
    } else {
      messagesHistory.forEach(function (msg) {
        appendMessageUI(msg.role, msg.text);
      });
      scrollToBottom();
    }

    // 4. Ecouteurs d'evenements
    triggerBtn.addEventListener('click', function () {
      chatBox.classList.toggle('open');
      scrollToBottom();
      if (chatBox.classList.contains('open')) {
        inputField.focus();
      }
    });

    closeBtn.addEventListener('click', function () {
      chatBox.classList.remove('open');
    });

    expandBtn.addEventListener('click', function () {
      chatBox.classList.toggle('expanded');
      if (chatBox.classList.contains('expanded')) {
        expandBtn.innerHTML = '❐';
        expandBtn.setAttribute('aria-label', 'Réduire le chat');
      } else {
        expandBtn.innerHTML = '⛶';
        expandBtn.setAttribute('aria-label', 'Agrandir le chat');
      }
      scrollToBottom();
    });

    resetBtn.addEventListener('click', function () {
      if (confirm('Voulez-vous vraiment commencer une nouvelle conversation ?')) {
        // Generate new session ID
        sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('brigitte_session_id', sessionId);
        
        // Clear UI
        messagesContainer.innerHTML = '';
        
        // Add initial message
        addMessage('assistant', 'Bonjour ! Je suis Brigitte, l\'assistante virtuelle de la mairie de Brignon-les-Bains. Comment puis-je vous aider aujourd\'hui ?', false);
        
        // Remove expanded class if active
        chatBox.classList.remove('expanded');
        expandBtn.innerHTML = '⛶';
        expandBtn.setAttribute('aria-label', 'Agrandir le chat');
        
        inputField.value = '';
        inputField.focus();
      }
    });

    sendBtn.addEventListener('click', function () {
      handleUserSubmit();
    });

    inputField.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        handleUserSubmit();
      }
    });

    suggestionBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var text = btn.getAttribute('data-text');
        handleUserSubmit(text);
      });
    });

    // 5. Fonctions internes
    function handleUserSubmit(text) {
      var query = (text || inputField.value).trim();
      if (!query) return;

      if (!text) {
        inputField.value = '';
      }

      addMessage('user', query);
      showLoading();

      fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          app_name: 'app',
          user_id: userId,
          session_id: sessionId,
          new_message: {
            role: 'user',
            parts: [{ text: query }]
          }
        })
      })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('Erreur réseau');
        }
        return response.json();
      })
      .then(function (events) {
        removeLoading();
        var assistantResponse = '';
        if (Array.isArray(events)) {
          events.forEach(function (evt) {
            if (evt.content && evt.content.parts) {
              evt.content.parts.forEach(function (part) {
                if (part.text) {
                  assistantResponse += part.text;
                }
              });
            }
          });
        }
        if (!assistantResponse) {
          assistantResponse = "Désolé, je n'ai pas pu formuler de réponse. Veuillez réessayer ou contacter le secrétariat.";
        }
        addMessage('assistant', assistantResponse);
      })
      .catch(function (error) {
        removeLoading();
        addMessage('system', 'Erreur : Impossible de joindre les serveurs de la mairie. Assurez-vous que le serveur de l\'agent (port 8000) est en cours d\'exécution.');
        console.error(error);
      });
    }

    function addMessage(role, text, save) {
      if (save !== false) {
        messagesHistory.push({ role: role, text: text });
        localStorage.setItem('brigitte_history_' + sessionId, JSON.stringify(messagesHistory));
      }
      appendMessageUI(role, text);
      scrollToBottom();
    }

    function appendMessageUI(role, text) {
      var msgDiv = document.createElement('div');
      msgDiv.className = 'chat-message ' + role;
      
      // Basic formatting for markdown bold, links, and bullet points in response
      var formatted = text
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #0f4c5c; text-decoration: underline; font-weight: bold;">$1</a>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^\*\s(.*)/gm, '• $1')
        .replace(/\n/g, '<br>');
        
      msgDiv.innerHTML = formatted;
      messagesContainer.appendChild(msgDiv);
    }

    function showLoading() {
      var loadingDiv = document.createElement('div');
      loadingDiv.className = 'chat-loading';
      loadingDiv.id = 'chat-loading-indicator';
      loadingDiv.innerHTML = 'Brigitte réfléchit <div class="chat-loading-dots"><span></span><span></span><span></span></div>';
      messagesContainer.appendChild(loadingDiv);
      scrollToBottom();
    }

    function removeLoading() {
      var loadingDiv = document.getElementById('chat-loading-indicator');
      if (loadingDiv) {
        loadingDiv.parentNode.removeChild(loadingDiv);
      }
    }

    function scrollToBottom() {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

});

