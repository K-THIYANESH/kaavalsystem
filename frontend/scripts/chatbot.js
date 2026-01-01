// AI Voice Assistant / Chatbot for KAAVAL with Tamil/English Support
// Using global API_BASE from window.KAAVAL_API_BASE (set in index.html)

class KAAVALChatbot {
  constructor() {
    this.isListening = false;
    this.recognition = null;
    this.messages = [];
    this.currentLanguage = 'ta'; // Tamil by default
    this.isMinimized = false;
    this.init();
  }

  init() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'ta-IN'; // Tamil by default

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.handleUserInput(transcript);
      };

      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.isListening = false;
        document.getElementById('chatbot-voice')?.setAttribute('title', 'Voice Input');
        document.getElementById('chatbot-voice').textContent = '🎤';
      };

      this.recognition.onend = () => {
        this.isListening = false;
        document.getElementById('chatbot-voice')?.setAttribute('title', 'Voice Input');
        document.getElementById('chatbot-voice').textContent = '🎤';
      };
    }

    this.createUI();
    this.loadInitialMessage();
  }

  createUI() {
    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'chatbot-toggle';
    toggleBtn.innerHTML = `
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        <path d="M13 8H7"/>
        <path d="M17 12H7"/>
      </svg>
    `;
    toggleBtn.title = 'Open KAAVAL AI Assistant';
    toggleBtn.id = 'chatbot-toggle';
    document.body.appendChild(toggleBtn);

    // Create chatbot container
    const chatbot = document.createElement('div');
    chatbot.id = 'kaaval-chatbot';
    chatbot.className = 'hidden';
    chatbot.innerHTML = `
      <div class="chatbot-header">
        <h3>KAAVAL Assistant</h3>
        <div style="display: flex; gap: 8px; align-items: center;">
          <button class="chatbot-minimize" id="chatbot-minimize" title="Minimize">−</button>
          <button class="chatbot-close" id="chatbot-close" title="Close">×</button>
        </div>
      </div>
      <div class="chatbot-lang-toggle">
        <button id="lang-tamil" class="active">தமிழ்</button>
        <button id="lang-english">English</button>
      </div>
      <div class="chatbot-messages" id="chatbot-messages"></div>
      <div class="chatbot-input">
        <input type="text" id="chatbot-input" placeholder="கேள்விகளை கேளுங்கள்...">
        <button id="chatbot-send">Send</button>
        <button id="chatbot-voice" title="Voice Input">🎤</button>
      </div>
    `;
    document.body.appendChild(chatbot);

    // Toggle chatbot
    toggleBtn.addEventListener('click', () => {
      chatbot.classList.remove('hidden');
      toggleBtn.style.display = 'none';
      document.getElementById('chatbot-input')?.focus();
    });

    // Minimize chatbot
    document.getElementById('chatbot-minimize')?.addEventListener('click', () => {
      chatbot.classList.add('hidden');
      toggleBtn.style.display = 'flex';
    });

    // Close chatbot
    document.getElementById('chatbot-close')?.addEventListener('click', () => {
      chatbot.classList.add('hidden');
      toggleBtn.style.display = 'flex';
    });

    // Language switching
    document.getElementById('lang-tamil')?.addEventListener('click', () => {
      this.switchLanguage('ta');
      document.getElementById('lang-tamil').classList.add('active');
      document.getElementById('lang-english').classList.remove('active');
    });

    document.getElementById('lang-english')?.addEventListener('click', () => {
      this.switchLanguage('en');
      document.getElementById('lang-english').classList.add('active');
      document.getElementById('lang-tamil').classList.remove('active');
    });

    document.getElementById('chatbot-send')?.addEventListener('click', () => {
      const input = document.getElementById('chatbot-input');
      if (input.value.trim()) {
        this.handleUserInput(input.value);
        input.value = '';
      }
    });

    document.getElementById('chatbot-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        document.getElementById('chatbot-send')?.click();
      }
    });

    document.getElementById('chatbot-voice')?.addEventListener('click', () => {
      this.toggleVoiceInput();
    });
  }

  switchLanguage(lang) {
    this.currentLanguage = lang;
    if (this.recognition) {
      this.recognition.lang = lang === 'ta' ? 'ta-IN' : 'en-US';
    }
    const input = document.getElementById('chatbot-input');
    if (input) {
      input.placeholder = lang === 'ta'
        ? 'கேள்விகளை கேளுங்கள்...'
        : 'Ask me anything about KAAVAL...';
    }
    // Reload initial message in new language
    const messagesContainer = document.getElementById('chatbot-messages');
    if (messagesContainer) {
      messagesContainer.innerHTML = '';
      this.loadInitialMessage();
    }
  }

  loadInitialMessage() {
    const message = this.currentLanguage === 'ta'
      ? 'வணக்கம்! நான் KAAVAL AI உதவியாளர். கணினியை எவ்வாறு பயன்படுத்துவது, காணாமல் போனவர்களை புகாரளிப்பது, தரவுத்தளத்தை தேடுவது போன்றவற்றில் உங்களுக்கு உதவ முடியும். இன்று நான் எவ்வாறு உதவ முடியும்?'
      : 'Hello! I\'m KAAVAL Assistant. I can help you understand how to use the system, report missing persons, search the database, and more. How can I assist you today?';
    this.addMessage('assistant', message);
  }

  addMessage(role, text) {
    const messagesContainer = document.getElementById('chatbot-messages');
    if (!messagesContainer) return;

    const message = document.createElement('div');
    message.className = `chatbot-message ${role}`;
    message.innerHTML = `<div class="message-content">${text}</div>`;
    messagesContainer.appendChild(message);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    if (role === 'assistant') {
      this.speak(text);
    }
  }

  async handleUserInput(input) {
    this.addMessage('user', input);
    const response = await this.generateResponse(input);
    this.addMessage('assistant', response);
  }

  async generateResponse(input) {
    const lowerInput = input.toLowerCase();
    const isTamil = this.currentLanguage === 'ta';

    // Tamil responses
    if (isTamil) {
      if (lowerInput.includes('காணாமல்') || lowerInput.includes('புகார்') || lowerInput.includes('missing') || lowerInput.includes('report')) {
        return 'காணாமல் போனவரை புகாரளிக்க, மேல் வலது மூலையில் "Login" என்பதை கிளிக் செய்து, "User Login" என்பதைத் தேர்ந்தெடுக்கவும். உள்நுழைந்த பிறகு, பெயர், வயது, கடைசியாக பார்க்கப்பட்ட இடம் போன்ற விவரங்களுடன் புகார் படிவத்தை நிரப்பி, புகைப்படத்தை பதிவேற்றலாம்.';
      }

      if (lowerInput.includes('கண்டுபிடி') || lowerInput.includes('found') || lowerInput.includes('காணப்படும்')) {
        return 'காணாமல் போனவரை நீங்கள் கண்டுபிடித்திருந்தால், உள்நுழைந்து "Report Found Person" தாவலைப் பயன்படுத்தவும். நீங்கள் ஆதார புகைப்படத்தை பதிவேற்றலாம் அல்லது புகைப்படம் இல்லையென்றால் நேரடியாக அதிகாரிகளைத் தொடர்பு கொள்ளலாம்.';
      }

      if (lowerInput.includes('தேடு') || lowerInput.includes('search') || lowerInput.includes('தரவுத்தளம்') || lowerInput.includes('database')) {
        return 'தரவுத்தளத்தைத் தேட, "Unidentified Bodies" பிரிவுக்குச் சென்று "Attribute-Aware Database Search" பயன்படுத்தவும். வயது, பாலினம், தோல் நிறம், முடி நிறம் போன்றவற்றால் வடிகட்டலாம்.';
      }

      if (lowerInput.includes('வீடியோ') || lowerInput.includes('video') || lowerInput.includes('பதிவேற்ற')) {
        return 'வீடியோவை பகுப்பாய்வு செய்ய, "Missing Persons" பிரிவுக்குச் சென்று "Video Intelligence" என்பதைக் கிளிக் செய்யவும். உங்கள் வீடியோ கோப்பை பதிவேற்றவும், கணினி தானாகவே பிரேம்களை பிரித்தெடுத்து, முகங்களை கண்டறிந்து, தரவுத்தளத்தில் பொருத்தங்களைத் தேடும்.';
      }

      if (lowerInput.includes('மீட்டமை') || lowerInput.includes('restore') || lowerInput.includes('reconstruct')) {
        return 'சேதமடைந்த முக படத்தை மீட்டமைக்க, "Unidentified Bodies" → "Decayed Face Restoration" க்குச் செல்லவும். சேதமடைந்த படத்தை பதிவேற்றவும், கணினி AI பயன்படுத்தி அதை மீட்டமைக்கும். வயது முன்னேற்ற படங்களையும் உருவாக்கலாம்.';
      }

      if (lowerInput.includes('கேமரா') || lowerInput.includes('camera') || lowerInput.includes('நேரடி') || lowerInput.includes('live')) {
        return 'நேரடி கேமரா கண்டறிதலைப் பயன்படுத்த, "Missing Persons" → "Live Watch" க்குச் சென்று "Start Stream" என்பதைக் கிளிக் செய்யவும். கணினி நேரத்தில் முகங்களை பகுப்பாய்வு செய்து, பொருத்தங்கள் கண்டறியப்படும்போது உங்களுக்கு அறிவிக்கும்.';
      }

      if (lowerInput.includes('உதவி') || lowerInput.includes('help') || lowerInput.includes('எப்படி') || lowerInput.includes('how')) {
        return 'KAAVAL க்கு இரண்டு முக்கிய பிரிவுகள் உள்ளன: 1) Missing Persons - நேரடி கேமரா கண்டறிதல் மற்றும் வீடியோ பகுப்பாய்வுக்கு, 2) Unidentified Bodies - முக மீட்டமைப்பு, வயது முன்னேற்றம் மற்றும் தரவுத்தள தேடலுக்கு. உள்நுழைந்து காணாமல் போனவர்கள் அல்லது கண்டுபிடிக்கப்பட்டவர்களைப் புகாரளிக்கலாம். எந்த அம்சத்தைப் பற்றி மேலும் அறிய விரும்புகிறீர்கள்?';
      }

      return 'நீங்கள் KAAVAL பற்றி கேட்கிறீர்கள் என்பதை நான் புரிந்துகொள்கிறேன். கணினி முக அங்கீகாரம், வீடியோ பகுப்பாய்வு மற்றும் தரவுத்தள தேடல் மூலம் காணாமல் போனவர்களைக் கண்டுபிடிக்க உதவுகிறது. காணாமல் போனவர்களைப் புகாரளிக்கலாம், வீடியோக்களை பகுப்பாய்வு செய்யலாம், சேதமடைந்த முகங்களை மீட்டமைக்கலாம் மற்றும் தரவுத்தளத்தைத் தேடலாம். எந்த அம்சத்தைப் பற்றி மேலும் உதவி விரும்புகிறீர்கள்?';
    }

    // English responses
    if (lowerInput.includes('missing person') || lowerInput.includes('report')) {
      return 'To report a missing person, click on "Login" in the top right, then select "User Login". After logging in, you can fill out the missing person report form with details like name, age, last seen location, and upload a photo.';
    }

    if (lowerInput.includes('found person') || lowerInput.includes('found someone')) {
      return 'If you found someone who might be a missing person, log in and use the "Report Found Person" tab. You can upload a proof photo or contact authorities directly if you don\'t have a photo.';
    }

    if (lowerInput.includes('search') || lowerInput.includes('database')) {
      return 'To search the database, go to the "Unidentified Bodies" section and use the "Attribute-Aware Database Search". You can filter by age, gender, skin tone, hair color, and more to narrow down results.';
    }

    if (lowerInput.includes('video') || lowerInput.includes('upload video')) {
      return 'To analyze a video, go to the "Missing Persons" section and click "Video Intelligence". Upload your video file, and the system will automatically extract frames, detect faces, and search for matches in the database.';
    }

    if (lowerInput.includes('restore') || lowerInput.includes('reconstruct')) {
      return 'To restore a damaged face image, go to "Unidentified Bodies" → "Decayed Face Restoration". Upload the damaged image, and the system will reconstruct it using AI. You can also generate age progression images.';
    }

    if (lowerInput.includes('camera') || lowerInput.includes('live')) {
      return 'To use live camera detection, go to "Missing Persons" → "Live Watch" and click "Start Stream". The system will analyze faces in real-time and alert you when matches are found.';
    }

    if (lowerInput.includes('help') || lowerInput.includes('how')) {
      return 'KAAVAL has two main sections: 1) Missing Persons - for live camera detection and video analysis, 2) Unidentified Bodies - for face restoration, age progression, and database search. You can also report missing or found persons by logging in. What would you like to know more about?';
    }

    return 'I understand you\'re asking about KAAVAL. The system helps locate missing persons through facial recognition, video analysis, and database search. You can report missing persons, analyze videos, restore damaged faces, and search the database. Would you like more specific help with any feature?';
  }

  speak(text) {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = this.currentLanguage === 'ta' ? 'ta-IN' : 'en-US';
      utterance.rate = this.currentLanguage === 'ta' ? 0.85 : 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Load voices and set Tamil voice if available
      const setVoice = () => {
        if (this.currentLanguage === 'ta') {
          const voices = speechSynthesis.getVoices();
          const tamilVoice = voices.find(voice =>
            voice.lang.startsWith('ta') ||
            voice.name.toLowerCase().includes('tamil') ||
            voice.name.toLowerCase().includes('india')
          );
          if (tamilVoice) {
            utterance.voice = tamilVoice;
          } else {
            // Fallback to any Indian English voice
            const indianVoice = voices.find(voice =>
              voice.lang.includes('IN') || voice.lang.includes('India')
            );
            if (indianVoice) utterance.voice = indianVoice;
          }
        }
        speechSynthesis.speak(utterance);
      };

      // If voices are already loaded
      if (speechSynthesis.getVoices().length > 0) {
        setVoice();
      } else {
        // Wait for voices to load
        speechSynthesis.onvoiceschanged = () => {
          setVoice();
        };
      }
    }
  }

  // Load voices when available
  loadVoices() {
    if ('speechSynthesis' in window) {
      const voices = speechSynthesis.getVoices();
      if (voices.length === 0) {
        speechSynthesis.onvoiceschanged = () => {
          this.loadVoices();
        };
      }
    }
  }

  toggleVoiceInput() {
    if (!this.recognition) {
      const message = this.currentLanguage === 'ta'
        ? 'உங்கள் உலாவியில் குரல் உள்ளீடு ஆதரிக்கப்படவில்லை.'
        : 'Voice input is not supported in your browser.';
      alert(message);
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      document.getElementById('chatbot-voice').textContent = '🎤';
      document.getElementById('chatbot-voice').setAttribute('title', this.currentLanguage === 'ta' ? 'குரல் உள்ளீடு' : 'Voice Input');
    } else {
      try {
        this.recognition.start();
        this.isListening = true;
        document.getElementById('chatbot-voice').textContent = '⏹️';
        document.getElementById('chatbot-voice').setAttribute('title', this.currentLanguage === 'ta' ? 'நிறுத்து' : 'Stop');
      } catch (error) {
        console.error('Error starting recognition:', error);
        this.isListening = false;
      }
    }
  }
}

// Initialize chatbot when page loads
let chatbotInstance = null;

function initChatbot() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (!chatbotInstance) {
        chatbotInstance = new KAAVALChatbot();
        chatbotInstance.loadVoices();
      }
    });
  } else {
    if (!chatbotInstance) {
      chatbotInstance = new KAAVALChatbot();
      chatbotInstance.loadVoices();
    }
  }
}

// Initialize chatbot
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initChatbot);
} else {
  initChatbot();
}

