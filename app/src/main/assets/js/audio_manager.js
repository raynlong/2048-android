function AudioManager() {
  this.ctx = null;
  this.enabled = true;
}

// Lazy-init AudioContext (needed for mobile autoplay policy)
AudioManager.prototype._getCtx = function () {
  if (!this.ctx) {
    var AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) {
      this.ctx = new AudioCtx();
    }
  }
  // Resume if suspended (mobile browsers)
  if (this.ctx && this.ctx.state === 'suspended') {
    this.ctx.resume();
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
  gain.gain.setValueAtTime(0.25, now);
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
  gain2.gain.setValueAtTime(0.1, now + 0.02);
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
  gain.gain.setValueAtTime(0.1, now);
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(now);
  osc.stop(now + 0.1);
};

// Singleton
window.audioManager = new AudioManager();
