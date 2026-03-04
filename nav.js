(function () {
  const APPS = [
    { label: '⚡ AI OS', href: 'index.html', match: ['', 'index.html'] },
    { label: '🐍 Snake', href: 'snake.html', match: ['snake.html'] },
    { label: '🧪 Lab', href: 'https://sinkrest.github.io/lab/', match: [], external: true },
  ];

  const page = window.location.pathname.split('/').pop();

  const style = document.createElement('style');
  style.textContent = `
    #aios-nav {
      position: sticky;
      top: 0;
      z-index: 999;
      display: flex;
      align-items: center;
      gap: .4rem;
      padding: .65rem 1.2rem;
      background: rgba(11, 22, 40, 0.94);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid rgba(255,255,255,0.06);
      font-family: 'Inter', -apple-system, sans-serif;
    }
    #aios-nav .aios-sep {
      flex: 1;
    }
    #aios-nav a {
      padding: .32rem .85rem;
      border-radius: 7px;
      text-decoration: none;
      font-size: .82rem;
      font-weight: 600;
      color: #8a9dba;
      border: 1px solid transparent;
      transition: color .2s, border-color .2s, background .2s;
      white-space: nowrap;
    }
    #aios-nav a:hover {
      color: #27c0e7;
      border-color: rgba(39,192,231,0.3);
      background: rgba(39,192,231,0.08);
    }
    #aios-nav a.aios-active {
      color: #27c0e7;
      border-color: rgba(39,192,231,0.35);
      background: rgba(39,192,231,0.1);
    }
    #aios-nav a.aios-ext::after {
      content: ' ↗';
      font-size: .7em;
      opacity: .55;
    }
  `;
  document.head.appendChild(style);

  const nav = document.createElement('nav');
  nav.id = 'aios-nav';

  APPS.forEach((app, i) => {
    // Insert spacer before external links to push them right
    if (app.external) {
      const sep = document.createElement('span');
      sep.className = 'aios-sep';
      nav.appendChild(sep);
    }

    const a = document.createElement('a');
    a.href = app.href;
    a.textContent = app.label;

    if (app.external) {
      a.target = '_blank';
      a.rel = 'noopener';
      a.className = 'aios-ext';
    }

    if (app.match.includes(page)) {
      a.className = (a.className ? a.className + ' ' : '') + 'aios-active';
    }

    nav.appendChild(a);
  });

  document.body.prepend(nav);
})();
