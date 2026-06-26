(function () {
  // 月亮图标（亮色时显示，点击切换暗色）
  var ICON_DARK = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#776e65" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  // 太阳图标（暗色时显示，点击切换亮色）
  var ICON_LIGHT = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#c9c0b3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

  var isDark = localStorage.getItem('2048-dark') === 'on';

  function applyDark(dark) {
    isDark = dark;
    if (dark) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    var btn = document.getElementById('dark-toggle');
    if (btn) {
      btn.innerHTML = dark ? ICON_LIGHT : ICON_DARK;
    }
    localStorage.setItem('2048-dark', dark ? 'on' : 'off');
  }

  // 尽早应用，防止闪白
  if (isDark) {
    document.documentElement.style.background = '#1a1a2e';
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyDark(isDark);
    var btn = document.getElementById('dark-toggle');
    if (btn) {
      btn.addEventListener('click', function () { applyDark(!isDark); });
      btn.addEventListener('touchend', function (e) {
        e.preventDefault();
        applyDark(!isDark);
      });
    }
  });
})();
