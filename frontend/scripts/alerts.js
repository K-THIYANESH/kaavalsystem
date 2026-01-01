const API_BASE = (typeof window !== 'undefined' && window.KAAVAL_API_BASE) ? window.KAAVAL_API_BASE : "http://localhost:8000/api";

class AlertSystem {
  constructor() {
    this.init();
  }

  init() {
    this.createAlertContainer();
    this.connectToAlertStream();
    this.setupNotificationPermission();
  }

  createAlertContainer() {
    const container = document.createElement("div");
    container.id = "alert-container";
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 400px;
    `;
    document.body.appendChild(container);
    this.alertContainer = container;
  }

  async setupNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
      await Notification.requestPermission();
    }
  }

  connectToAlertStream() {
    try {
      this.eventSource = new EventSource(`${API_BASE}/alerts/stream`);

      this.eventSource.onmessage = (event) => {
        const alert = JSON.parse(event.data);
        this.handleAlert(alert);
      };

      this.eventSource.onerror = (error) => {
        console.error("Alert stream error:", error);
        // Reconnect after 5 seconds
        setTimeout(() => this.connectToAlertStream(), 5000);
      };
    } catch (error) {
      console.error("Failed to connect to alert stream:", error);
    }
  }

  handleAlert(alert) {
    // Show browser notification
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification("KAAVAL Match Alert", {
        body: `Strong match found: ${alert.person_name} (${(alert.confidence * 100).toFixed(1)}%)`,
        icon: "/favicon.ico",
        tag: `alert-${alert.id}`,
      });
    }

    // Show in-page alert
    this.showInPageAlert(alert);

    // Play sound
    this.playAlertSound();
  }

  showInPageAlert(alert) {
    const alertElement = document.createElement("div");
    alertElement.className = "alert-banner";
    alertElement.style.cssText = `
      background: linear-gradient(135deg, rgba(32, 227, 178, 0.95), rgba(32, 227, 178, 0.85));
      color: var(--bg);
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      animation: slideIn 0.3s ease;
      cursor: pointer;
      border-left: 4px solid #fff;
    `;

    alertElement.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start; gap: 12px;">
        <div style="flex: 1;">
          <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">
            🚨 Strong Match Detected
          </div>
          <div style="font-size: 14px; opacity: 0.95;">
            <strong>${alert.person_name}</strong> - ${(alert.confidence * 100).toFixed(1)}% confidence
          </div>
          ${alert.location ? `<div style="font-size: 12px; margin-top: 4px; opacity: 0.9;">📍 ${alert.location}</div>` : ""}
        </div>
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          cursor: pointer;
          font-size: 18px;
          line-height: 1;
        ">×</button>
      </div>
    `;

    this.alertContainer.appendChild(alertElement);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (alertElement.parentNode) {
        alertElement.style.animation = "slideOut 0.3s ease";
        setTimeout(() => alertElement.remove(), 300);
      }
    }, 10000);

    // Click to acknowledge
    alertElement.addEventListener("click", async () => {
      await this.acknowledgeAlert(alert.id);
      alertElement.remove();
    });
  }

  playAlertSound() {
    // Create a simple beep sound
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = "sine";

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  }

  async acknowledgeAlert(alertId) {
    try {
      await fetch(`${API_BASE}/alerts/acknowledge/${alertId}`, {
        method: "POST",
      });
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  }

  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

// Add CSS animations
const style = document.createElement("style");
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Initialize alert system
let alertSystem = null;
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    alertSystem = new AlertSystem();
  });
} else {
  alertSystem = new AlertSystem();
}

// Export for manual alert creation (for testing)
window.createTestAlert = async (personName, confidence) => {
  try {
    const response = await fetch(`${API_BASE}/alerts/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        person_id: 1,
        person_name: personName,
        confidence: confidence,
        match_type: "live_camera",
        location: "Test Location",
      }),
    });
    return await response.json();
  } catch (error) {
    console.error("Failed to create test alert:", error);
  }
};

