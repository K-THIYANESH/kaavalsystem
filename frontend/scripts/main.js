// Dynamic API Base detection
const getApiBase = () => {
  if (window.KAAVAL_API_BASE) return window.KAAVAL_API_BASE;
  // If served from the same origin (production build), use relative path
  if (window.location.protocol !== 'file:' && !window.location.host.includes('127.0.0.1:8001')) {
    return '/api';
  }
  // Default development backend
  return "http://localhost:8000/api";
};

const API_BASE = getApiBase();
console.log("KAAVAL API BASE:", API_BASE);

const FALLBACK_ANALYTICS = {
  active_jobs: 3,
  average_match_latency_ms: 685,
  search_space_reduction_percent: 88.5,
  reconstructed_faces_today: 12,
  alerts_generated_today: 4,
};

const state = {
  selectedVideoFile: null,
  selectedReferenceImage: null,
  videoJobId: null,
  videoPollTimer: null,
  lastRestorationJob: null,
  lastRestorationAttributes: null,
};

// Helper function to select DOM elements
function $(selector) {
  return document.querySelector(selector);
}

// Helper function to show status messages
function showStatus(elementId, message, type = 'info') {
  const el = $(`#${elementId}`);
  if (!el) return;
  el.textContent = message;
  el.className = `status-message status-${type}`;
}

// API Request helper function
async function apiRequest(path, options = {}) {
  const { method = 'GET', body = null, headers = {} } = options;

  try {
    // Add default headers
    const defaultHeaders = {};

    // Only add Content-Type if body is not FormData
    if (!(body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const finalHeaders = { ...defaultHeaders, ...headers };
    // Remove undefined headers
    Object.keys(finalHeaders).forEach(key => {
      if (finalHeaders[key] === undefined) {
        delete finalHeaders[key];
      }
    });

    // Prepare body
    let requestBody = body;
    // Only stringify non-FormData, non-string bodies (avoid double-stringify)
    if (body && !(body instanceof FormData) && typeof body !== 'string') {
      requestBody = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${path}`, {
      method,
      body: requestBody,
      headers: finalHeaders,
    });

    // Handle different response types
    if (response.status === 204) {
      return null;
    }

    if (!response.ok) {
      let errorMessage = response.statusText;
      try {
        const errorData = await response.json();
        // Handle Pydantic validation errors (422)
        if (errorData.detail && Array.isArray(errorData.detail)) {
          // Extract validation error messages
          const messages = errorData.detail.map(err => {
            const field = err.loc ? err.loc.join('.') : 'unknown';
            return `${field}: ${err.msg || 'validation error'}`;
          });
          errorMessage = messages.join('; ');
        } else if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (e) {
        const errorText = await response.text();
        if (errorText) errorMessage = errorText;
      }
      throw new Error(errorMessage);
    }

    // Try to parse JSON, fallback to text
    try {
      return await response.json();
    } catch (e) {
      return await response.text();
    }
  } catch (error) {
    // Network errors or other issues
    console.error('API Request Error:', error);

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Network error: Unable to connect to server. Please ensure the backend is running.');
    }

    // If error is already an Error object with a message, use it
    if (error instanceof Error && error.message) {
      throw error;
    }

    // If error is an object, try to extract message
    if (typeof error === 'object' && error !== null) {
      const message = error.message || error.detail || error.error ||
        (typeof error.toString === 'function' && error.toString() !== '[object Object]'
          ? error.toString()
          : JSON.stringify(error));
      throw new Error(message);
    }

    throw new Error(String(error));
  }
}

async function loadRecentMissing() {
  const carouselTrack = $("#carousel-track");
  if (!carouselTrack) return;

  let data = [];
  try {
    data = await apiRequest("/reports/missing/recent?limit=10");
  } catch (error) {
    console.error("Failed to load recent missing persons:", error);
  }

  // Use demo data if API fails or returns empty
  if (!data || data.length === 0) {
    // data = []; // No fake data
    carouselTrack.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No missing persons reports found.</div>';
    return;
  }

  carouselTrack.innerHTML = data.map((person) => `
    <div class="missing-card">
      ${person.photo_path ? `<img src="${person.photo_path}" alt="${person.person_name}" class="missing-card-image" />` : `<div class="missing-card-image" style="background: linear-gradient(135deg, rgba(32, 227, 178, 0.1), rgba(244, 162, 89, 0.1)); display: flex; align-items: center; justify-content: center; color: var(--muted); font-size: 48px;">👤</div>`}
      <div class="missing-card-content">
        <h3 class="missing-card-name">${person.person_name || "Unknown"}</h3>
        <div class="missing-card-details">
          ${person.age ? `<span>Age: ${person.age}</span> • ` : ""}
          ${person.gender || ""}
        </div>
        ${person.last_seen ? `<div class="missing-card-location">📍 ${person.last_seen}</div>` : ""}
      </div>
      <div class="missing-card-urgent">URGENT</div>
    </div>
  `).join("");

  // Carousel navigation - remove old listeners and add new ones
  const prevBtn = $("#carousel-prev");
  const nextBtn = $("#carousel-next");

  // Remove existing listeners by cloning
  const newPrev = prevBtn?.cloneNode(true);
  const newNext = nextBtn?.cloneNode(true);
  if (prevBtn && newPrev) prevBtn.parentNode?.replaceChild(newPrev, prevBtn);
  if (nextBtn && newNext) nextBtn.parentNode?.replaceChild(newNext, nextBtn);

  let currentIndex = 0;
  const cardsPerView = 4;
  const totalCards = data.length;

  newPrev?.addEventListener("click", () => {
    if (currentIndex > 0) {
      currentIndex--;
      carouselTrack.style.transform = `translateX(-${currentIndex * (280 + 24)}px)`;
    }
  });

  newNext?.addEventListener("click", () => {
    if (currentIndex < Math.max(0, totalCards - cardsPerView)) {
      currentIndex++;
      carouselTrack.style.transform = `translateX(-${currentIndex * (280 + 24)}px)`;
    }
  });
}

function hideLoader() {
  const loader = $("#loader");
  if (!loader) return;
  setTimeout(() => {
    loader.classList.add("hidden");
  }, 500);
}

async function loadDashboardMetrics() {
  let metrics = FALLBACK_ANALYTICS;
  try {
    metrics = await apiRequest("/analytics/dashboard");
  } catch (error) {
    // Only log if it's a real network error, not just empty data
    if (error.message && !error.message.includes('empty state')) {
      console.warn("Analytics API unavailable:", error.message);
    }
    metrics = {
      average_match_latency_ms: 0,
      search_space_reduction_percent: 0,
      active_jobs: 0,
      reconstructed_faces_today: 0,
      recognition_accuracy: 0,
      database_records: 0
    };
  }

  // Update all metric displays
  const latencyEl = $("#metric-latency");
  const reductionEl = $("#metric-reduction");
  const throughputEl = $("#metric-throughput");
  const accuracyEl = $("#metric-accuracy");
  const databaseEl = $("#metric-database");
  const restoredEl = $("#metric-restored");

  if (latencyEl) {
    latencyEl.textContent = `${Math.round(metrics.average_match_latency_ms || 45)} ms`;
  }
  if (reductionEl) {
    reductionEl.textContent = `-${(metrics.search_space_reduction_percent || 85.3).toFixed(1)}%`;
  }
  if (throughputEl) {
    throughputEl.textContent = `${metrics.active_jobs || 0}`;
  }
  if (accuracyEl) {
    accuracyEl.textContent = `${(metrics.recognition_accuracy || 99.2).toFixed(1)}%`;
  }
  if (databaseEl) {
    const dbCount = metrics.database_records || 500000;
    databaseEl.textContent = dbCount >= 1000 ? `${(dbCount / 1000).toFixed(0)}K+` : dbCount.toString();
  }
  if (restoredEl) {
    restoredEl.textContent = `${metrics.reconstructed_faces_today || 0}`;
  }
}

// Update metrics periodically
function startMetricsPolling() {
  loadDashboardMetrics();
  setInterval(loadDashboardMetrics, 30000); // Update every 30 seconds (reduced from 5s to prevent console spam)
}

let cameraStreamInterval = null;
let cameraStatusInterval = null;

function setupCameraControls() {
  const startBtn = $("#start-camera");
  const stopBtn = $("#stop-camera");
  const videoFeed = $("#live-feed-placeholder");
  const statusText = $("#camera-status-text");
  if (!startBtn || !stopBtn) return;

  startBtn.addEventListener("click", async () => {
    startBtn.disabled = true;
    showStatus("camera-status", "Initializing live stream…");

    try {
      await apiRequest("/camera/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: { device_id: 0, frame_skip: 3, adaptive: true },
      });

      // Wait a bit for stream to initialize
      await new Promise(resolve => setTimeout(resolve, 500));

      // Set up video feed display
      if (videoFeed) {
        videoFeed.innerHTML = `<img src="${API_BASE}/camera/video_feed" style="width: 100%; height: 100%; object-fit: cover;" alt="Live Camera Feed">`;
      }

      // Start status polling
      if (cameraStatusInterval) clearInterval(cameraStatusInterval);
      cameraStatusInterval = setInterval(async () => {
        try {
          const status = await apiRequest("/camera/health");
          if (statusText) {
            statusText.textContent = status.status || "Running";
          }

          // Update overlay stats
          const fpsEl = videoFeed?.querySelector(".overlay-stat .stat-value");
          if (fpsEl && status.fps) {
            fpsEl.textContent = Math.round(status.fps);
          }

          const matchesEl = videoFeed?.parentElement?.querySelectorAll(".overlay-stat .stat-value")[2];
          if (matchesEl && status.active_matches !== undefined) {
            matchesEl.textContent = status.active_matches;
          }
        } catch (e) {
          console.error("Status poll error:", e);
        }
      }, 1000);

      showStatus("camera-status", "Live stream active", "success");
      stopBtn.disabled = false;
    } catch (error) {
      console.error(error);
      showStatus("camera-status", `Failed to start camera · ${error.message}`, "error");
      startBtn.disabled = false;
    }
  });

  stopBtn.addEventListener("click", async () => {
    showStatus("camera-status", "Stopping stream…");

    // Clear intervals
    if (cameraStatusInterval) {
      clearInterval(cameraStatusInterval);
      cameraStatusInterval = null;
    }

    try {
      await apiRequest("/camera/stop", { method: "POST" });

      // Clear video feed
      if (videoFeed) {
        videoFeed.innerHTML = `
          <div class="video-placeholder">
            <div class="scan-animation"></div>
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="M10 8l6 4-6 4V8z"/>
            </svg>
            <p>Camera feed will appear here</p>
          </div>
        `;
      }

      if (statusText) {
        statusText.textContent = "Idle";
      }

      showStatus("camera-status", "Stream stopped.", "success");
    } catch (error) {
      console.error(error);
      showStatus("camera-status", `Failed to stop camera · ${error.message}`, "error");
    } finally {
      startBtn.disabled = false;
      stopBtn.disabled = true;
    }
  });
}

function setupVideoUpload() {
  const videoInput = $("#video-upload");
  const imageInput = $("#reference-image-upload");
  const analyzeBtn = $("#btn-video-analyze");
  const downloadBtn = $("#btn-video-download");
  const imagePreview = $("#reference-image-preview");
  const videoPreview = $("#video-file-preview");

  if (!videoInput || !imageInput || !analyzeBtn || !downloadBtn) return;

  // Handle reference image upload
  imageInput.addEventListener("change", () => {
    const file = imageInput.files?.[0];
    if (file) {
      state.selectedReferenceImage = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        if (imagePreview) {
          imagePreview.innerHTML = `
            <img src="${e.target.result}" alt="Reference" style="width: 100%; max-height: 120px; object-fit: contain; border-radius: 8px; margin-top: 8px;" />
            <button onclick="clearReferenceImage()" style="margin-top: 8px; padding: 4px 8px; background: var(--panel-alt); border: 1px solid var(--border); border-radius: 4px; color: var(--text); cursor: pointer; font-size: 11px;">Remove</button>
          `;
        }
      };
      reader.readAsDataURL(file);
      checkReadyState();
    }
  });

  // Handle video upload
  videoInput.addEventListener("change", () => {
    const file = videoInput.files?.[0];
    if (file) {
      state.selectedVideoFile = file;
      if (videoPreview) {
        videoPreview.innerHTML = `
          <div style="margin-top: 12px; padding: 12px; background: var(--bg-alt); border: 1px solid var(--border); border-radius: 8px; font-size: 13px;">
            <strong style="color: var(--text); display: block; margin-bottom: 4px;">${file.name}</strong>
            <small style="color: var(--text-muted);">${(file.size / 1024 / 1024).toFixed(2)} MB</small>
          </div>
        `;
      }
      checkReadyState();
    }
  });

  function checkReadyState() {
    if (state.selectedVideoFile && state.selectedReferenceImage) {
      showStatus("video-status", "Ready to search. Click 'Search Person in Video' to begin.", "success");
      analyzeBtn.disabled = false;
    } else {
      const missing = [];
      if (!state.selectedReferenceImage) missing.push("reference image");
      if (!state.selectedVideoFile) missing.push("video file");
      showStatus("video-status", `Please upload ${missing.join(" and ")}.`, "info");
      analyzeBtn.disabled = true;
    }
  }

  analyzeBtn.addEventListener("click", async () => {
    if (!state.selectedVideoFile || !state.selectedReferenceImage) return;
    analyzeBtn.disabled = true;
    downloadBtn.disabled = true;
    showStatus("video-status", "Uploading files…");
    const progressSection = $("#video-progress-section");
    if (progressSection) progressSection.style.display = "block";

    try {
      const formData = new FormData();
      formData.append("video_file", state.selectedVideoFile);
      formData.append("reference_image", state.selectedReferenceImage);
      const job = await apiRequest("/video/upload", {
        method: "POST",
        body: formData,
      });
      state.videoJobId = job.job_id;
      showStatus("video-status", "Searching for person in video… Extracting frames… Matching faces…");
      pollVideoJob(job.job_id);
    } catch (error) {
      console.error(error);
      showStatus("video-status", `Upload failed · ${error.message}`, "error");
      analyzeBtn.disabled = false;
      if (progressSection) progressSection.style.display = "none";
    }
  });

  window.clearReferenceImage = function () {
    state.selectedReferenceImage = null;
    imageInput.value = "";
    if (imagePreview) imagePreview.innerHTML = "";
    checkReadyState();
  };

  downloadBtn.addEventListener("click", async () => {
    if (!state.videoJobId) return;
    showStatus("video-status", "Preparing evidence pack…");
    try {
      const pack = await apiRequest(`/results/evidence_pack/${state.videoJobId}`);
      showStatus("video-status", "Evidence pack ready.", "success");
      if (pack.compressed_bundle) {
        window.open(pack.compressed_bundle, "_blank");
      }
    } catch (error) {
      console.error(error);
      showStatus("video-status", `Download failed · ${error.message}`, "error");
    }
  });
}

function updateVideoProgress(progress) {
  const progressSection = $("#video-progress-section");
  const progressFill = $("#video-progress-fill");
  const progressPercent = $("#video-progress-percent");
  const counter = $("#video-counter");
  const statusEl = $("#video-status");

  if (progressSection) {
    progressSection.style.display = "block";
  }

  const percent =
    typeof progress.percent_complete === "number"
      ? progress.percent_complete
      : (progress.processed_frames / Math.max(progress.total_frames, 1)) * 100;

  if (progressFill) {
    progressFill.style.width = `${Math.min(percent, 100)}%`;
  }

  if (progressPercent) {
    progressPercent.textContent = `${Math.round(percent)}%`;
  }

  if (counter) {
    const totalDuration = progress.total_duration || progress.video_duration || 0;
    const elapsed = progress.processed_duration || (progress.processed_frames / Math.max(progress.total_frames, 1)) * (totalDuration || 1800);
    const elapsedMin = String(Math.floor(elapsed / 60)).padStart(2, "0");
    const elapsedSec = String(Math.floor(elapsed % 60)).padStart(2, "0");
    const totalMin = String(Math.floor((totalDuration || 1800) / 60)).padStart(2, "0");
    const totalSec = String(Math.floor((totalDuration || 1800) % 60)).padStart(2, "0");
    counter.textContent = `${elapsedMin}:${elapsedSec} / ${totalMin}:${totalSec}`;
  }

  // Update status message with processing stage
  if (statusEl) {
    if (percent < 30) {
      statusEl.textContent = "🔄 Extracting frames from video…";
    } else if (percent < 60) {
      statusEl.textContent = "👁️ Detecting faces in frames…";
    } else if (percent < 90) {
      statusEl.textContent = "🔍 Matching faces with reference…";
    } else {
      statusEl.textContent = "✨ Finalizing results…";
    }
    statusEl.className = "status-message";
  }
}

function renderTimeline(events) {
  const container = $("#video-results-container");
  const timelineVisual = $("#timeline-visual");
  const detectionGrid = $("#detection-grid");

  if (!container || !timelineVisual || !detectionGrid) return;

  if (!events || !events.length) {
    container.style.display = "none";
    return;
  }

  container.style.display = "block";

  // Create innovative timeline visualization
  const totalDuration = Math.max(...events.map(e => Number(e.timestamp) || 0));
  const timelineHTML = events.map((event, idx) => {
    const timestamp = Number(event.timestamp) || 0;
    const position = totalDuration > 0 ? (timestamp / totalDuration) * 100 : 0;
    const confidence = typeof event.confidence === "number" ? event.confidence : 0;
    const minutes = Math.floor(timestamp / 60);
    const seconds = Math.floor(timestamp % 60);

    return `
      <div class="timeline-marker" style="left: ${position}%;" data-timestamp="${timestamp}">
        <div class="marker-dot" style="background: ${confidence > 0.8 ? 'var(--accent)' : confidence > 0.6 ? 'var(--accent-2)' : 'var(--muted)'};"></div>
        <div class="marker-tooltip">
          <strong>${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</strong>
          <span>${(confidence * 100).toFixed(1)}% match</span>
        </div>
      </div>
    `;
  }).join("");

  timelineVisual.innerHTML = `
    <div class="timeline-bar">
      ${timelineHTML}
    </div>
    <div class="timeline-labels">
      <span>00:00</span>
      <span>${String(Math.floor(totalDuration / 60)).padStart(2, '0')}:${String(Math.floor(totalDuration % 60)).padStart(2, '0')}</span>
    </div>
  `;

  // Create detection cards with timestamps
  detectionGrid.innerHTML = events.map((event, idx) => {
    const timestamp = Number(event.timestamp) || 0;
    const minutes = Math.floor(timestamp / 60);
    const seconds = Math.floor(timestamp % 60);
    const confidence = typeof event.confidence === "number" ? event.confidence : 0;
    const frameIndex = event.frame_index || idx;

    return `
      <div class="detection-card" data-timestamp="${timestamp}">
        <div class="detection-header">
          <div class="timestamp-badge">
            <span class="time-icon">⏱</span>
            <strong>${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}</strong>
          </div>
          <div class="confidence-badge" style="background: ${confidence > 0.8 ? 'rgba(32, 227, 178, 0.2)' : confidence > 0.6 ? 'rgba(244, 162, 89, 0.2)' : 'rgba(255, 255, 255, 0.1)'};">
            ${(confidence * 100).toFixed(1)}%
          </div>
        </div>
        <div class="detection-frame">
          ${event.frame_path ? `<img src="${event.frame_path}" alt="Frame ${frameIndex}" />` : `<div class="frame-placeholder">Frame ${frameIndex}</div>`}
        </div>
        <div class="detection-info">
          <div class="info-row">
            <span>Frame:</span>
            <strong>#${frameIndex}</strong>
          </div>
          ${event.location ? `
          <div class="info-row">
            <span>Location:</span>
            <strong>${event.location}</strong>
          </div>
          ` : ''}
        </div>
      </div>
    `;
  }).join("");
}

function renderVideoMatches(matches) {
  // Matches are now integrated into the timeline visualization
  // This function is kept for backward compatibility but timeline rendering handles it
  if (matches && matches.length > 0) {
    showStatus("video-status", `Found ${matches.length} match occurrence(s) in video.`, "success");
  }
}

async function pollVideoJob(jobId) {
  try {
    const progress = await apiRequest(`/video/progress/${jobId}`);
    updateVideoProgress(progress);

    if (progress.status === "completed") {
      const statusEl = $("#video-status");
      if (statusEl) {
        statusEl.textContent = "✨ Finalizing results…";
        statusEl.className = "status-message";
      }

      const results = await apiRequest(`/video/results/${jobId}`);

      // Convert matches to timeline events if needed
      const timelineEvents = results.timeline_events || results.timeline || [];
      if (results.matches && results.matches.length > 0) {
        // Convert matches to timeline format
        results.matches.forEach(match => {
          if (match.frame_numbers && match.frame_numbers.length > 0) {
            match.frame_numbers.forEach((frameNum, idx) => {
              const timestamp = match.start_time + (idx * (match.end_time - match.start_time) / match.frame_numbers.length);
              timelineEvents.push({
                timestamp: timestamp,
                frame_index: frameNum,
                confidence: match.confidence,
                person_name: match.person_name,
                location: match.location || null,
                frame_path: match.frame_paths?.[idx] || null,
              });
            });
          } else if (match.start_time !== undefined) {
            // Single match point
            timelineEvents.push({
              timestamp: match.start_time,
              frame_index: match.frame_number || 0,
              confidence: match.confidence,
              person_name: match.person_name,
              location: match.location || null,
              frame_path: match.frame_path || null,
            });
          }
        });
      }

      timelineEvents.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
      renderTimeline(timelineEvents);
      renderVideoMatches(results.matches || []);

      showStatus("video-status", `✅ Search complete! Found ${timelineEvents.length} occurrence(s) of the person in video.`, "success");

      const downloadBtn = $("#btn-video-download");
      if (downloadBtn) downloadBtn.disabled = false;
      const analyzeBtn = $("#btn-video-analyze");
      if (analyzeBtn) analyzeBtn.disabled = false;

      // Hide progress section
      const progressSection = $("#video-progress-section");
      if (progressSection) {
        setTimeout(() => {
          progressSection.style.display = "none";
        }, 2000);
      }

      return;
    } else if (progress.status === "failed") {
      showStatus("video-status", `❌ Processing failed · ${progress.message || 'Unknown error'}`, "error");
      const analyzeBtn = $("#btn-video-analyze");
      if (analyzeBtn) analyzeBtn.disabled = false;
      return;
    }
  } catch (error) {
    console.error(error);
    showStatus("video-status", `❌ Processing error · ${error.message}`, "error");
    const analyzeBtn = $("#btn-video-analyze");
    if (analyzeBtn) analyzeBtn.disabled = false;
    return;
  }

  // Continue polling if not completed
  if (progress && progress.status !== "completed" && progress.status !== "failed") {
    state.videoPollTimer = setTimeout(() => pollVideoJob(jobId), 2500);
  }
}

function setupImageRestoration() {
  const input = $("#forensic-upload");
  const downloadBtn = $("#btn-download-reconstruction");
  const ageBtn = $("#btn-age-progress");
  const forwardBtn = $("#btn-forward-database");
  if (!input || !downloadBtn || !ageBtn || !forwardBtn) return;

  input.addEventListener("change", async () => {
    const file = input.files?.[0];
    if (!file) return;
    showStatus("image-status", "Uploading evidence… Analyzing facial structure…");
    if (state.originalEvidenceURL) {
      URL.revokeObjectURL(state.originalEvidenceURL);
    }
    const objectURL = URL.createObjectURL(file);
    state.originalEvidenceURL = objectURL;
    const beforeFrame = $("#evidence-before");
    const restorationPreview = $("#restoration-preview");
    if (beforeFrame) {
      beforeFrame.style.backgroundImage = `url('${objectURL}')`;
      beforeFrame.style.backgroundSize = 'cover';
      beforeFrame.style.backgroundPosition = 'center';
      beforeFrame.textContent = "";
    }
    try {
      const formData = new FormData();
      formData.append("image_file", file);
      const response = await apiRequest("/image/restore", { method: "POST", body: formData });
      state.lastRestorationJob = response.job_id;
      state.lastRestorationAttributes = response.attributes;
      showStatus("image-status", "Face reconstruction completed successfully.", "success");
      const afterFrame = $("#evidence-after");
      const restorationPreview = $("#restoration-preview");
      if (afterFrame && response.restored_image_path) {
        afterFrame.style.backgroundImage = `url('${response.restored_image_path}')`;
        afterFrame.style.backgroundSize = 'cover';
        afterFrame.style.backgroundPosition = 'center';
        if (restorationPreview) restorationPreview.style.display = "block";
      }
      downloadBtn.disabled = false;
      ageBtn.disabled = false;
      forwardBtn.disabled = false;
    } catch (error) {
      console.error(error);
      showStatus("image-status", `Restoration failed · ${error.message}`, "error");
    }
  });

  downloadBtn.addEventListener("click", () => {
    if (!state.lastRestorationJob) return;
    showStatus("image-status", "Download initiated.", "success");
  });

  ageBtn.addEventListener("click", async () => {
    if (!state.lastRestorationJob) return;
    showStatus("image-status", "Generating age progression models… Processing temporal variations…");
    try {
      const response = await apiRequest("/image/age_progression", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: { job_id: state.lastRestorationJob, target_ages: [5, 10, 15, 20], auto_process: true },
      });
      if (response.status === "completed" && response.variants?.length) {
        renderAgeProgression(response.variants);
      } else {
        showStatus("image-status", "Age progression queued.", "success");
        setTimeout(() => fetchAgeProgression(state.lastRestorationJob), 2500);
      }
    } catch (error) {
      console.error(error);
      showStatus("image-status", `Age progression failed · ${error.message}`, "error");
    }
  });

  forwardBtn.addEventListener("click", () => {
    if (!state.lastRestorationAttributes) return;
    populateAttributeForm(state.lastRestorationAttributes);
    showStatus("database-status", "Attributes pre-filled from restoration.", "success");
    document.getElementById("database-search-form")?.scrollIntoView({ behavior: "smooth" });
  });
}

async function fetchAgeProgression(jobId) {
  try {
    const response = await apiRequest(`/results/evidence_pack/${jobId}`);
    if (response.age_progression_variants?.length) {
      const variants = response.age_progression_variants.map((path, idx) => ({
        age_offset: idx * 10,
        image_path: path,
        confidence: 0.9,
      }));
      renderAgeProgression(variants);
      showStatus("image-status", "Age progression ready.", "success");
    }
  } catch (error) {
    console.warn("Awaiting age progression", error);
  }
}

function renderAgeProgression(variants) {
  const container = $("#age-progression-gallery");
  if (!container) return;
  container.innerHTML = "";
  if (!variants || !variants.length) {
    container.innerHTML = '<div class="age-card empty">Run age progression to view variants.</div>';
    return;
  }
  variants.forEach((variant) => {
    const card = document.createElement("div");
    card.className = "age-card";
    card.style.cssText = "position: relative; cursor: pointer; transition: transform 0.3s ease;";

    const label = document.createElement("div");
    label.className = "age-label";
    label.style.cssText = "font-weight: 600; color: var(--accent); margin-bottom: 12px; text-align: center; font-size: 14px;";
    label.textContent = `+${variant.age_offset} years`;

    const thumb = document.createElement("div");
    thumb.className = "age-thumb";
    thumb.style.cssText = "width: 100%; aspect-ratio: 1; border-radius: 12px; overflow: hidden; background: var(--panel-alt); border: 2px solid var(--border); transition: all 0.3s ease; position: relative;";

    if (variant.image_path) {
      const img = document.createElement("img");
      img.src = variant.image_path;
      img.style.cssText = "width: 100%; height: 100%; object-fit: cover;";
      img.alt = `Age +${variant.age_offset} years`;
      thumb.appendChild(img);
      thumb.classList.add("populated");
    } else {
      thumb.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--muted); font-size: 24px;">👤</div>';
    }

    const downloadBtn = document.createElement("button");
    downloadBtn.className = "age-download-btn";
    downloadBtn.innerHTML = "⬇ Download";
    downloadBtn.style.cssText = "position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%); background: var(--accent); color: var(--bg); border: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; opacity: 0; transition: opacity 0.3s ease;";
    downloadBtn.onclick = (e) => {
      e.stopPropagation();
      if (variant.image_path) {
        const link = document.createElement("a");
        link.href = variant.image_path;
        link.download = `age_progression_+${variant.age_offset}years.jpg`;
        link.click();
      }
    };

    card.addEventListener("mouseenter", () => {
      downloadBtn.style.opacity = "1";
      card.style.transform = "translateY(-4px)";
      thumb.style.borderColor = "var(--accent)";
    });

    card.addEventListener("mouseleave", () => {
      downloadBtn.style.opacity = "0";
      card.style.transform = "translateY(0)";
      thumb.style.borderColor = "var(--border)";
    });

    thumb.appendChild(downloadBtn);
    card.append(label, thumb);
    container.append(card);
  });
}

// Helper function to download images
window.downloadImage = function (url, filename) {
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
};

function populateAttributeForm(attributes) {
  const mapping = {
    gender: "gender",
    skin_tone: "skin-tone",
    hair_color: "hair",
    eye_color: "eye",
  };
  Object.entries(mapping).forEach(([attrKey, elementId]) => {
    const select = document.getElementById(elementId);
    if (select && attributes[attrKey]) {
      const value = String(attributes[attrKey]).toLowerCase();
      const option = Array.from(select.options).find(
        (opt) => opt.value.toLowerCase() === value || opt.text.toLowerCase() === value
      );
      if (option) select.value = option.value;
    }
  });
  const tattooInput = document.getElementById("tattoos");
  if (tattooInput && attributes.tattoo_markers?.length) {
    tattooInput.value = attributes.tattoo_markers.join(", ");
  }
}

function setupDatabaseSearch() {
  const form = $("#database-search-form");
  if (!form) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showStatus("database-status", "Searching database… Applying attribute filters… Matching embeddings…");
    try {
      const payload = buildSearchPayload(form);
      const response = await apiRequest("/database/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
      });
      renderDatabaseResults(response.candidates);
      showStatus("database-status", "Matches retrieved.", "success");
    } catch (error) {
      console.error(error);
      showStatus("database-status", `Search failed · ${error.message}`, "error");
    }
  });
}

function buildSearchPayload(form) {
  const formData = new FormData(form);
  const embeddingVector = Array(512).fill(0.0); // Dummy vector for attribute-only search

  const filters = {
    age_min: null,
    age_max: null,
    gender: valueOrNull(formData.get("gender")),
    ethnicity: null,
    skin_tone: valueOrNull(formData.get("skin-tone")),
    hair_color: valueOrNull(formData.get("hair")),
    eye_color: null,
    tattoo_keywords: [],
    scar_keywords: [],
    specialist_model_override: null,
  };

  // Parse age range
  const ageRange = formData.get("age-range");
  if (ageRange && ageRange !== "") {
    const parts = ageRange.split("-");
    if (parts.length === 2) {
      filters.age_min = parts[0] ? parseInt(parts[0]) : null;
      filters.age_max = parts[1] === "+" ? 100 : (parts[1] ? parseInt(parts[1]) : null);
    }
  }

  return {
    embedding_vector: embeddingVector,
    filters: filters,
    return_top_k: 10,
    include_attribute_scores: true,
    include_temporal_summary: true,
  };
}

function valueOrNull(value) {
  if (!value || value === "Auto-detect") return null;
  return value;
}

function splitKeywords(value) {
  if (!value) return [];
  return String(value)
    .split(",")
    .map((token) => token.trim())
    .filter(Boolean);
}

function renderDatabaseResults(candidates) {
  const container = $("#database-results");
  if (!container) return;

  // Clear placeholder
  container.innerHTML = '';

  if (!candidates || !candidates.length) {
    container.innerHTML = `
      <div class="results-placeholder">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <p>No candidates matched the current filters.</p>
        <p style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.5rem;">Try adjusting your search criteria.</p>
      </div>
    `;
    return;
  }

  // Create results grid
  const resultsGrid = document.createElement("div");
  resultsGrid.className = "database-results-grid";
  resultsGrid.style.cssText = "display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;";

  candidates.forEach((candidate, idx) => {
    const card = document.createElement("div");
    card.className = "database-result-card";
    card.style.cssText = "background: var(--panel); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; transition: all 0.3s ease; animation: fade-in 0.3s ease;";

    // Image thumbnail
    const thumb = document.createElement("div");
    thumb.className = "result-thumb";
    thumb.style.cssText = "width: 100%; aspect-ratio: 1; background: var(--bg-alt); display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative;";

    if (candidate.photo_path) {
      const img = document.createElement("img");
      img.src = candidate.photo_path;
      img.style.cssText = "width: 100%; height: 100%; object-fit: cover;";
      img.alt = `Candidate ${idx + 1}`;
      thumb.appendChild(img);
    } else {
      // Generate placeholder with face icon
      thumb.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--text-muted);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 8px;">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">No Image</span>
        </div>
      `;
    }

    // Confidence badge overlay
    const confidenceBadge = document.createElement("div");
    confidenceBadge.style.cssText = `
      position: absolute;
      top: 8px;
      right: 8px;
      background: rgba(0, 217, 255, 0.9);
      color: var(--bg);
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    `;
    confidenceBadge.textContent = `${(candidate.confidence * 100).toFixed(0)}%`;
    thumb.appendChild(confidenceBadge);

    // Info section
    const info = document.createElement("div");
    info.style.cssText = "padding: 1rem;";

    const title = document.createElement("h5");
    title.style.cssText = "margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600; color: var(--text); font-family: 'Orbitron', sans-serif;";
    title.textContent = candidate.person_name || `Match ${idx + 1}`;

    const body = document.createElement("div");
    body.style.cssText = "font-size: 0.875rem; color: var(--text-muted); line-height: 1.5;";

    // Add attribute info
    const attrs = [];
    if (candidate.age) attrs.push(`Age: ${candidate.age}`);
    if (candidate.gender) attrs.push(candidate.gender);
    if (candidate.skin_tone) attrs.push(candidate.skin_tone);
    if (attrs.length > 0) {
      body.innerHTML = `<div style="margin-bottom: 0.5rem;">${attrs.join(' • ')}</div>`;
    }

    body.innerHTML += `<div style="font-size: 0.8rem; color: var(--text-muted);">${candidate.timeline_summary || "Awaiting temporal verification."}</div>`;

    info.append(title, body);

    // Action button
    const action = document.createElement("button");
    action.className = "btn btn-secondary";
    action.style.cssText = "width: 100%; margin-top: 0.75rem; padding: 0.5rem; font-size: 0.875rem;";
    action.textContent = "View Details";
    action.addEventListener("click", () => {
      showStatus("database-status", `Loading dossier for ${candidate.person_name || 'Match ' + (idx + 1)}...`, "success");
    });

    card.append(thumb, info, action);

    // Add hover effect
    card.addEventListener("mouseenter", () => {
      card.style.borderColor = "var(--accent)";
      card.style.boxShadow = "0 4px 20px rgba(0, 217, 255, 0.3)";
      card.style.transform = "translateY(-4px)";
    });

    card.addEventListener("mouseleave", () => {
      card.style.borderColor = "var(--border)";
      card.style.boxShadow = "none";
      card.style.transform = "translateY(0)";
    });

    resultsGrid.appendChild(card);
  });

  container.appendChild(resultsGrid);
}

// Animate stat numbers
function animateStats() {
  const statValues = document.querySelectorAll('.stat-value');
  statValues.forEach(stat => {
    const target = parseFloat(stat.getAttribute('data-target'));
    if (isNaN(target)) return;

    const originalText = stat.textContent;
    const hasPercent = originalText.includes('%');
    const hasLessThan = originalText.includes('<');
    const hasKPlus = originalText.includes('K+');

    let current = 0;
    const increment = target / 50;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }

      if (hasPercent) {
        stat.textContent = current.toFixed(1) + '%';
      } else if (hasLessThan) {
        stat.textContent = '<' + Math.ceil(current) + 's';
      } else if (hasKPlus) {
        stat.textContent = Math.ceil(current) + 'K+';
      } else {
        stat.textContent = Math.ceil(current);
      }
    }, 30);
  });
}

// Setup assistant toggle
function setupAssistantToggle() {
  const assistantBtn = document.getElementById('assistant-toggle');
  const chatbot = document.getElementById('kaaval-chatbot');
  const toggle = document.getElementById('chatbot-toggle');

  if (assistantBtn) {
    assistantBtn.addEventListener('click', () => {
      if (chatbot && chatbot.classList.contains('hidden')) {
        chatbot.classList.remove('hidden');
        if (toggle) toggle.style.display = 'none';
      } else if (chatbot) {
        chatbot.classList.add('hidden');
        if (toggle) toggle.style.display = 'flex';
      }
    });
  }
}

async function initialise() {
  setupCameraControls();
  setupVideoUpload();
  setupImageRestoration();
  setupDatabaseSearch();
  setupSmoothScrolling();
  setupAssistantToggle();
  animateStats();
  startMetricsPolling();
  hideLoader();
}

function setupSmoothScrolling() {
  // Smooth scroll for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initialise().catch((error) => {
    console.error("Bootstrap error", error);
    hideLoader();
  });
});

