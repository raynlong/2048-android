function AudioManager() {
  this.ctx = null;
  this.enabled = true;
  this._initialized = false;
}

// One-time init triggered by first user touch
AudioManager.prototype._boot = function () {
  if (this._initialized) return;
  this._initialized = true;
  var AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtx) return;
  try {
    this.ctx = new AudioCtx();
  } catch (e) {
    return;
  }
  // Resume on Android WebView — must happen inside user gesture
  if (this.ctx.state === 'suspended') {
    var self = this;
    this.ctx.resume().then(function () {
      // Play a silent buffer to fully unlock audio
      var buf = self.ctx.createBuffer(1, 1, 22050);
      var src = self.ctx.createBufferSource();
      src.buffer = buf;
      src.connect(self.ctx.destination);
      src.start(0);
    }).catch(function () {});
  }
};

// Try to lock audio on first user interaction (touch / click)
// Listens on both document & game-container for reliability
AudioManager.prototype._lock = function () {
  var self = this;
  var handler = function () {
    self._boot();
    document.removeEventListener('touchstart', handler, true);
    document.removeEventListener('mousedown', handler, true);
  };
  // Use capture phase so it fires even if gameContainer calls preventDefault
  document.addEventListener('touchstart', handler, true);
  document.addEventListener('mousedown', handler, true);
};

// Get audio context — always returns ctx if possible, queues audio when suspended
AudioManager.prototype._getCtx = function () {
  if (!this._initialized) this._boot();
  if (!this.ctx) return null;
  if (this.ctx.state !== 'running') {
    this.ctx.resume().catch(function () {});
    // Return ctx anyway — audio nodes queue until context is running
  }
  return this.ctx;
};

// Play a merge chime — pitch rises with tile value
AudioManager.prototype.playMerge = function (value) {
  if (!this.enabled) return;
  var ctx = this._getCtx();
  if (!ctx) return;

  // Base frequency scales logarithmically with tile value
  // 2 => ~330Hz, 2048 => ~880Hz, super tiles go higher
  var baseFreq = 220 + Math.log2(value) * 55;
  var now = ctx.currentTime;

  // Main tone: short sine blip
  var osc = ctx.createOscillator();
  var gain = ctx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(baseFreq, now);
  osc.frequency.exponentialRampToValueAtTime(baseFreq * 1.5, now + 0.06);
  osc.frequency.exponentialRampToValueAtTime(baseFreq * 0.8, now + 0.1);
  gain.gain.setValueAtTime(0.5, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(now);
  osc.stop(now + 0.15);

  // Harmonic overtone for richness
  var osc2 = ctx.createOscillator();
  var gain2 = ctx.createGain();
  osc2.type = 'sine';
  osc2.frequency.setValueAtTime(baseFreq * 2, now + 0.02);
  gain2.gain.setValueAtTime(0.2, now + 0.02);
  gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
  osc2.connect(gain2);
  gain2.connect(ctx.destination);
  osc2.start(now + 0.02);
  osc2.stop(now + 0.18);
};

// A crisp slide tick — quick, satisfying feedback
AudioManager.prototype.playMove = function () {
  if (!this.enabled) return;
  var ctx = this._getCtx();
  if (!ctx) return;
  var now = ctx.currentTime;

  // Brief low-frequency thump
  var osc = ctx.createOscillator();
  var gain = ctx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(180, now);
  osc.frequency.exponentialRampToValueAtTime(280, now + 0.03);
  osc.frequency.exponentialRampToValueAtTime(120, now + 0.07);
  gain.gain.setValueAtTime(0.2, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(now);
  osc.stop(now + 0.1);
};

// Singleton — auto-lock on first touch
window.audioManager = new AudioManager();
window.audioManager._lock();

// Sound toggle: read from localStorage, wire the button
(function () {
  var saved = localStorage.getItem('2048-sound');
  if (saved === 'off') {
    window.audioManager.enabled = false;
  }
  var ICON_ON  = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#776e65" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
  var ICON_OFF = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#776e65" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';
  function syncUI() {
    var btn = document.getElementById('sound-toggle');
    if (btn) {
      btn.innerHTML = window.audioManager.enabled ? ICON_ON : ICON_OFF;
    }
  }
  // Wait for DOM
  document.addEventListener('DOMContentLoaded', function () {
    syncUI();
    var btn = document.getElementById('sound-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        window.audioManager.enabled = !window.audioManager.enabled;
        localStorage.setItem('2048-sound', window.audioManager.enabled ? 'on' : 'off');
        syncUI();
      });
      btn.addEventListener('touchend', function (e) {
        e.preventDefault();
        window.audioManager.enabled = !window.audioManager.enabled;
        localStorage.setItem('2048-sound', window.audioManager.enabled ? 'on' : 'off');
        syncUI();
      });
    }
  });
})();
