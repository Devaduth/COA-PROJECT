/* ═══════════════════════════════════════════════════════════
   ProcessorSim — Application Logic, Animations & Charts
   ═══════════════════════════════════════════════════════════ */

// ─── Chart.js Global Defaults (Dark Theme) ───
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
Chart.defaults.font.family = "'Inter', sans-serif";

const CHART_COLORS = {
  primary:  '#6366f1',
  blue:     '#3b82f6',
  green:    '#10b981',
  orange:   '#f59e0b',
  purple:   '#8b5cf6',
  cyan:     '#22d3ee',
  red:      '#ef4444',
  pink:     '#ec4899',
};

// ─── State ───
const state = {
  lenis: null,
  charts: {},
  stallMode: 'none',
  cacheMode: 'single',
  reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
};

// ═══════════════════════════════════════════
//  INITIALIZATION
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initPreloader();
  initLenis();
  initCustomCursor();
  initGSAP();
  initNavigation();
  initScrollProgress();
  initTheoryToggles();
  initPillGroups();
  initCardSpotlight();
  initMagneticButtons();
  initRippleEffect();
  initHeroParticles();
  initScrollToTop();
  initFooterReveal();
});

// ═══════════════════════════════════════════
//  PRELOADER
// ═══════════════════════════════════════════
function initPreloader() {
  const preloader = document.getElementById('preloader');
  if (!preloader) return;
  if (state.reducedMotion) { preloader.classList.add('done'); return; }
  window.addEventListener('load', () => {
    gsap.to(preloader, {
      opacity: 0, duration: 0.6, delay: 1.2, ease: 'power2.inOut',
      onComplete: () => { preloader.classList.add('done'); }
    });
  });
  // Safety fallback — hide after 4s no matter what
  setTimeout(() => preloader.classList.add('done'), 4000);
}

// ═══════════════════════════════════════════
//  CUSTOM CURSOR
// ═══════════════════════════════════════════
function initCustomCursor() {
  if (state.reducedMotion || 'ontouchstart' in window) return;
  const dot = document.getElementById('cursorDot');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;

  let mx = -100, my = -100;
  document.addEventListener('mousemove', (e) => {
    mx = e.clientX; my = e.clientY;
    gsap.to(dot, { x: mx, y: my, duration: 0.08, ease: 'power2.out' });
    gsap.to(ring, { x: mx, y: my, duration: 0.25, ease: 'power2.out' });
  });

  // Hover effect on interactive elements
  const hoverEls = document.querySelectorAll('a, button, input, .feature-card, .pill, .nav-link');
  hoverEls.forEach(el => {
    el.addEventListener('mouseenter', () => ring.classList.add('hovering'));
    el.addEventListener('mouseleave', () => ring.classList.remove('hovering'));
  });
}

// ═══════════════════════════════════════════
//  LENIS SMOOTH SCROLL
// ═══════════════════════════════════════════
function initLenis() {
  try {
    state.lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
    });

    state.lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((time) => state.lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  } catch (e) {
    console.warn('Lenis init failed, using native scroll:', e);
  }
}

// ═══════════════════════════════════════════
//  SCROLL PROGRESS BAR
// ═══════════════════════════════════════════
function initScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  const main = document.getElementById('main');
  if (!bar || !main) return;

  const update = () => {
    const scrollTop = main.scrollTop || window.scrollY;
    const scrollHeight = main.scrollHeight - main.clientHeight || document.documentElement.scrollHeight - window.innerHeight;
    const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    bar.style.width = pct + '%';
  };

  window.addEventListener('scroll', update, { passive: true });
  main.addEventListener('scroll', update, { passive: true });
}

// ═══════════════════════════════════════════
//  GSAP ANIMATIONS
// ═══════════════════════════════════════════
function initGSAP() {
  gsap.registerPlugin(ScrollTrigger);

  // ── Hero text split animation ──
  const heroTitle = document.querySelector('.hero-title[data-split]');
  if (heroTitle && !state.reducedMotion) {
    splitTextIntoWords(heroTitle);
    const words = heroTitle.querySelectorAll('.word');
    gsap.to(words, {
      y: 0, opacity: 1, rotateX: 0,
      duration: 0.9, stagger: 0.06, ease: 'power3.out', delay: 0.4,
    });
  }

  // ── Hero entrance (non-split items) ──
  const heroItems = document.querySelectorAll('#heroContent .anim-item:not([data-split])');
  gsap.fromTo(heroItems,
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.9, stagger: 0.15, ease: 'power3.out', delay: 0.3 }
  );

  // ── Hero parallax ──
  if (!state.reducedMotion) {
    gsap.to('.hero-bg-grid', {
      yPercent: 30, ease: 'none',
      scrollTrigger: { trigger: '.hero-section', start: 'top top', end: 'bottom top', scrub: true }
    });
    gsap.to('.hero-glow', {
      yPercent: 50, scale: 1.2, ease: 'none',
      scrollTrigger: { trigger: '.hero-section', start: 'top top', end: 'bottom top', scrub: true }
    });
  }

  // ── Feature cards stagger ──
  const featureCards = document.querySelectorAll('#featureGrid .anim-item');
  gsap.fromTo(featureCards,
    { opacity: 0, y: 50, scale: 0.95 },
    {
      opacity: 1, y: 0, scale: 1, duration: 0.7, stagger: 0.12,
      ease: 'power3.out', delay: 0.6,
    }
  );

  // ── Section reveal animations ──
  const sections = ['performance', 'pipeline', 'cache', 'amdahl'];
  sections.forEach(id => {
    const section = document.getElementById(id);
    if (!section) return;

    // Section header
    const headerItems = section.querySelectorAll('.section-header .anim-item');
    if (headerItems.length) {
      gsap.fromTo(headerItems,
        { opacity: 0, y: 30 },
        {
          opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: 'power3.out',
          scrollTrigger: { trigger: section, start: 'top 80%', toggleActions: 'play none none none' },
        }
      );
    }

    // Cards
    const cards = section.querySelectorAll(':scope > .container > .content-grid .anim-item, :scope > .container > .theory-card.anim-item, :scope > .container > .charts-grid .anim-item, :scope > .container > .glass-card.anim-item:not(.theory-card)');
    if (cards.length) {
      gsap.fromTo(cards,
        { opacity: 0, y: 40 },
        {
          opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out',
          scrollTrigger: { trigger: section, start: 'top 70%', toggleActions: 'play none none none' },
        }
      );
    }
  });
}

// ─── Animate results appearing ───
function animateResults(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.style.display = '';
  gsap.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });

  const metrics = el.querySelectorAll('.metric-card');
  gsap.fromTo(metrics,
    { opacity: 0, y: 15, scale: 0.95 },
    { opacity: 1, y: 0, scale: 1, duration: 0.4, stagger: 0.06, ease: 'power3.out', delay: 0.15,
      onComplete: () => animateCounters(el),
    }
  );
}

function animateCharts(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.style.display = '';
  gsap.fromTo(el, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' });

  const cards = el.querySelectorAll('.chart-card, .glass-card');
  gsap.fromTo(cards,
    { opacity: 0, y: 25, scale: 0.97 },
    { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.1, ease: 'power3.out', delay: 0.1 }
  );
}

// ═══════════════════════════════════════════
//  TEXT SPLIT HELPER
// ═══════════════════════════════════════════
function splitTextIntoWords(el) {
  const processNode = (node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const words = node.textContent.split(/(\s+)/);
      const frag = document.createDocumentFragment();
      words.forEach(word => {
        if (word.trim() === '') {
          frag.appendChild(document.createTextNode(word));
        } else {
          const wrap = document.createElement('span');
          wrap.className = 'word-wrap';
          const inner = document.createElement('span');
          inner.className = 'word';
          inner.textContent = word;
          inner.style.transform = 'translateY(110%) rotateX(-15deg)';
          inner.style.opacity = '0';
          wrap.appendChild(inner);
          frag.appendChild(wrap);
        }
      });
      return frag;
    }
    return null;
  };

  const children = [...el.childNodes];
  children.forEach(child => {
    if (child.nodeType === Node.TEXT_NODE) {
      const frag = processNode(child);
      if (frag) el.replaceChild(frag, child);
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      // For child elements like .gradient-text, split inside them
      const innerChildren = [...child.childNodes];
      innerChildren.forEach(inner => {
        if (inner.nodeType === Node.TEXT_NODE) {
          const frag = processNode(inner);
          if (frag) child.replaceChild(frag, inner);
        }
      });
    }
  });
  // Force visibility of the parent
  el.style.opacity = '1';
}

// ═══════════════════════════════════════════
//  CARD SPOTLIGHT (cursor-following glow)
// ═══════════════════════════════════════════
function initCardSpotlight() {
  document.querySelectorAll('[data-tilt]').forEach(card => {
    const spotlight = card.querySelector('.card-spotlight');
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      if (spotlight) {
        spotlight.style.setProperty('--x', x + 'px');
        spotlight.style.setProperty('--y', y + 'px');
      }
      if (!state.reducedMotion) {
        const rotX = ((y / rect.height) - 0.5) * -8;
        const rotY = ((x / rect.width) - 0.5) * 8;
        gsap.to(card, { rotateX: rotX, rotateY: rotY, duration: 0.4, ease: 'power2.out', transformPerspective: 800 });
      }
    });
    card.addEventListener('mouseleave', () => {
      gsap.to(card, { rotateX: 0, rotateY: 0, duration: 0.6, ease: 'elastic.out(1, 0.5)' });
    });
  });
}

// ═══════════════════════════════════════════
//  MAGNETIC BUTTONS
// ═══════════════════════════════════════════
function initMagneticButtons() {
  if (state.reducedMotion) return;
  document.querySelectorAll('.magnetic').forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const dx = e.clientX - (rect.left + rect.width / 2);
      const dy = e.clientY - (rect.top + rect.height / 2);
      gsap.to(btn, { x: dx * 0.2, y: dy * 0.2, duration: 0.3, ease: 'power2.out' });
    });
    btn.addEventListener('mouseleave', () => {
      gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.4)' });
    });
  });
}

// ═══════════════════════════════════════════
//  RIPPLE EFFECT
// ═══════════════════════════════════════════
function initRippleEffect() {
  document.querySelectorAll('.btn-primary').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'btn-ripple';
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

// ═══════════════════════════════════════════
//  HERO PARTICLES
// ═══════════════════════════════════════════
function initHeroParticles() {
  if (state.reducedMotion) return;
  const container = document.getElementById('heroParticles');
  if (!container) return;
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.top = Math.random() * 100 + '%';
    container.appendChild(p);
    gsap.to(p, {
      y: -80 - Math.random() * 120,
      x: (Math.random() - 0.5) * 60,
      opacity: 0.3 + Math.random() * 0.4,
      duration: 3 + Math.random() * 4,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
      delay: Math.random() * 3,
    });
  }
}

// ═══════════════════════════════════════════
//  SCROLL TO TOP
// ═══════════════════════════════════════════
function initScrollToTop() {
  const btn = document.getElementById('scrollTop');
  if (!btn) return;

  const toggleVisibility = () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    btn.classList.toggle('visible', scrollTop > 400);
  };
  window.addEventListener('scroll', toggleVisibility, { passive: true });

  btn.addEventListener('click', () => {
    if (state.lenis) {
      state.lenis.scrollTo(0, { duration: 1.5 });
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
}

// ═══════════════════════════════════════════
//  FOOTER REVEAL
// ═══════════════════════════════════════════
function initFooterReveal() {
  const footer = document.querySelector('.footer-reveal');
  if (!footer) return;
  ScrollTrigger.create({
    trigger: footer,
    start: 'top 95%',
    onEnter: () => footer.classList.add('revealed'),
    once: true,
  });
}

// ═══════════════════════════════════════════
//  ANIMATED COUNTER
// ═══════════════════════════════════════════
function animateCounters(container) {
  if (state.reducedMotion) return;
  const values = container.querySelectorAll('.metric-value');
  values.forEach(el => {
    const text = el.textContent.trim();
    const match = text.match(/^([\d,.]+)/);
    if (!match) return;
    const target = parseFloat(match[1].replace(/,/g, ''));
    if (isNaN(target) || target === 0) return;
    const suffix = text.replace(match[1], '');
    const hasDecimals = match[1].includes('.');
    const decimals = hasDecimals ? (match[1].split('.')[1] || '').length : 0;
    el.textContent = '0' + suffix;
    gsap.to({ val: 0 }, {
      val: target,
      duration: 1.2,
      ease: 'power2.out',
      onUpdate: function () {
        const v = this.targets()[0].val;
        el.textContent = (decimals > 0 ? v.toFixed(decimals) : Math.round(v).toLocaleString()) + suffix;
      },
    });
  });
}

// ═══════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════
function initNavigation() {
  const links = document.querySelectorAll('.nav-link');
  const menuBtn = document.getElementById('menuBtn');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const featureCards = document.querySelectorAll('.feature-card[data-nav]');

  // Sidebar nav links
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const sectionId = link.getAttribute('data-section');
      setActiveNav(sectionId);
      scrollToSection(sectionId);
      closeMobileMenu();
    });
  });

  // Feature card clicks
  featureCards.forEach(card => {
    card.addEventListener('click', (e) => {
      e.preventDefault();
      const sectionId = card.getAttribute('data-nav');
      setActiveNav(sectionId);
      scrollToSection(sectionId);
    });
  });

  // Mobile menu toggle
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('show');
    });
  }
  if (overlay) overlay.addEventListener('click', closeMobileMenu);

  // Intersection observer for scroll-spy
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        setActiveNav(entry.target.id);
      }
    });
  }, { rootMargin: '-20% 0px -60% 0px' });

  document.querySelectorAll('.section').forEach(s => observer.observe(s));
}

function setActiveNav(id) {
  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.toggle('active', l.getAttribute('data-section') === id);
  });
}

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (!el) return;
  if (state.lenis) {
    state.lenis.scrollTo(el, { offset: -20, duration: 1.2 });
  } else {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}

function closeMobileMenu() {
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('sidebarOverlay')?.classList.remove('show');
}

// ═══════════════════════════════════════════
//  THEORY TOGGLES
// ═══════════════════════════════════════════
function initTheoryToggles() {
  document.querySelectorAll('.theory-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', !expanded);
      btn.parentElement.querySelector('.theory-content').classList.toggle('open');
    });
  });
}

// ═══════════════════════════════════════════
//  PILL GROUPS (stall mode, cache mode)
// ═══════════════════════════════════════════
function initPillGroups() {
  // Generic pill-slider positioning helper
  function positionSlider(group) {
    const slider = group.querySelector('.pill-slider');
    const active = group.querySelector('.pill.active');
    if (!slider || !active) return;
    const groupRect = group.getBoundingClientRect();
    const activeRect = active.getBoundingClientRect();
    slider.style.width = activeRect.width + 'px';
    slider.style.transform = `translateX(${activeRect.left - groupRect.left - 4}px)`;
  }

  // Stall mode pills
  const stallGroup = document.getElementById('stallModeGroup');
  if (stallGroup) {
    positionSlider(stallGroup);
    stallGroup.querySelectorAll('.pill').forEach(pill => {
      pill.addEventListener('click', () => {
        stallGroup.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.stallMode = pill.dataset.value;
        positionSlider(stallGroup);
        document.getElementById('manualControls').style.display = state.stallMode === 'manual' ? '' : 'none';
        document.getElementById('randomControls').style.display = state.stallMode === 'random' ? '' : 'none';
      });
    });
  }

  // Cache mode pills
  const cacheGroup = document.getElementById('cacheModeGroup');
  if (cacheGroup) {
    positionSlider(cacheGroup);
    cacheGroup.querySelectorAll('.pill').forEach(pill => {
      pill.addEventListener('click', () => {
        cacheGroup.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.cacheMode = pill.dataset.value;
        positionSlider(cacheGroup);
        document.getElementById('singleCacheInputs').style.display = state.cacheMode === 'single' ? '' : 'none';
        document.getElementById('multiCacheInputs').style.display = state.cacheMode === 'multi' ? '' : 'none';
      });
    });
  }

  // Reposition on resize
  window.addEventListener('resize', () => {
    if (stallGroup) positionSlider(stallGroup);
    if (cacheGroup) positionSlider(cacheGroup);
  });
}

// ═══════════════════════════════════════════
//  INSTRUCTION ROW MANAGEMENT
// ═══════════════════════════════════════════
function addInstrRow() {
  const container = document.getElementById('instrRows');
  const row = document.createElement('div');
  row.className = 'instr-row';
  row.innerHTML = `
    <input type="text" class="form-input instr-name" placeholder="Type">
    <input type="number" class="form-input instr-count" value="100" min="0" placeholder="Count">
    <input type="number" class="form-input instr-cpi" value="1" min="0.1" step="0.1" placeholder="CPI">
    <button class="btn-icon btn-remove" onclick="removeInstrRow(this)" title="Remove">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>`;
  container.appendChild(row);
  gsap.fromTo(row, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.3 });
}

function removeInstrRow(btn) {
  const rows = document.querySelectorAll('.instr-row');
  if (rows.length <= 1) return;
  const row = btn.closest('.instr-row');
  gsap.to(row, {
    opacity: 0, x: 10, height: 0, margin: 0, padding: 0,
    duration: 0.25, ease: 'power2.in',
    onComplete: () => row.remove(),
  });
}

// ═══════════════════════════════════════════
//  CHART HELPERS
// ═══════════════════════════════════════════
function destroyChart(key) {
  if (state.charts[key]) { state.charts[key].destroy(); delete state.charts[key]; }
}

function createChart(canvasId, config, key) {
  destroyChart(key);
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) return null;
  state.charts[key] = new Chart(ctx, config);
  return state.charts[key];
}

function tooltipConfig() {
  return {
    backgroundColor: 'rgba(10,10,18,0.95)',
    titleColor: '#e2e8f0',
    bodyColor: '#94a3b8',
    borderColor: 'rgba(255,255,255,0.08)',
    borderWidth: 1,
    cornerRadius: 8,
    padding: 12,
    titleFont: { weight: '600' },
  };
}

// ═══════════════════════════════════════════
//  PERFORMANCE CALCULATOR
// ═══════════════════════════════════════════
function calculatePerformance() {
  const clockNs = parseFloat(document.getElementById('perfClockNs').value) || 0.5;
  const rows = document.querySelectorAll('.instr-row');
  const categories = [];

  rows.forEach(row => {
    const name  = row.querySelector('.instr-name').value.trim() || 'Unknown';
    const count = parseInt(row.querySelector('.instr-count').value) || 0;
    const cpi   = parseFloat(row.querySelector('.instr-cpi').value) || 1;
    categories.push({ name, count, cpi });
  });

  const totalInstr = categories.reduce((s, c) => s + c.count, 0);
  if (totalInstr === 0) return;

  const totalCycles = categories.reduce((s, c) => s + c.count * c.cpi, 0);
  const avgCPI = totalCycles / totalInstr;
  const execTimeSec = totalCycles * clockNs * 1e-9;
  const mips = execTimeSec > 0 ? totalInstr / (execTimeSec * 1e6) : 0;

  // ── Render metrics ──
  const metricsHTML = [
    { label: 'Total Instructions', value: totalInstr.toLocaleString(), accent: '' },
    { label: 'Average CPI', value: avgCPI.toFixed(4), accent: 'accent-cyan' },
    { label: 'Total Cycles', value: totalCycles.toLocaleString(undefined, { maximumFractionDigits: 2 }), accent: '' },
    { label: 'Exec Time (s)', value: execTimeSec.toExponential(4), accent: 'accent-purple' },
    { label: 'MIPS', value: mips.toFixed(2), accent: 'accent-green' },
  ].map(m => `<div class="metric-card ${m.accent}"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`).join('');

  document.getElementById('perfMetrics').innerHTML = metricsHTML;
  animateResults('perfResults');

  // ── Charts ──
  const names = categories.map(c => c.name);
  const cpis = categories.map(c => c.cpi);
  const execCycles = categories.map(c => c.count * c.cpi);
  const counts = categories.map(c => c.count);

  // CPI vs Exec Cycles (Bar)
  createChart('cpiChart', {
    type: 'bar',
    data: {
      labels: names,
      datasets: [
        { label: 'CPI', data: cpis, backgroundColor: CHART_COLORS.blue + 'cc', borderRadius: 6, barPercentage: 0.5, yAxisID: 'y' },
        { label: 'Exec Cycles', data: execCycles, backgroundColor: CHART_COLORS.red + 'cc', borderRadius: 6, barPercentage: 0.5, yAxisID: 'y1' },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { tooltip: tooltipConfig(), legend: { labels: { padding: 16 } } },
      scales: {
        y:  { position: 'left', title: { display: true, text: 'CPI', color: CHART_COLORS.blue }, ticks: { color: CHART_COLORS.blue } },
        y1: { position: 'right', title: { display: true, text: 'Exec Cycles', color: CHART_COLORS.red }, ticks: { color: CHART_COLORS.red }, grid: { drawOnChartArea: false } },
      },
    },
  }, 'cpiChart');

  // Instruction Mix (Doughnut)
  const doughnutColors = [CHART_COLORS.blue, CHART_COLORS.red, CHART_COLORS.green, CHART_COLORS.orange, CHART_COLORS.purple, CHART_COLORS.cyan, CHART_COLORS.pink];
  createChart('instrMixChart', {
    type: 'doughnut',
    data: {
      labels: names,
      datasets: [{
        data: counts,
        backgroundColor: doughnutColors.slice(0, names.length),
        borderColor: '#06060a',
        borderWidth: 3,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '55%',
      plugins: {
        tooltip: tooltipConfig(),
        legend: { position: 'bottom', labels: { padding: 14, usePointStyle: true, pointStyle: 'circle' } },
      },
    },
  }, 'instrMixChart');

  // MIPS at various clock speeds
  const clockOptions = [0.25, 0.5, 1.0, 2.0, 4.0];
  const mipsValues = clockOptions.map(clk => {
    const t = totalCycles * clk * 1e-9;
    return t > 0 ? totalInstr / (t * 1e6) : 0;
  });

  createChart('perfCompChart', {
    type: 'bar',
    data: {
      labels: clockOptions.map(c => c + ' ns'),
      datasets: [{
        label: 'MIPS',
        data: mipsValues,
        backgroundColor: mipsValues.map((_, i) => {
          const colors = [CHART_COLORS.blue, CHART_COLORS.primary, CHART_COLORS.purple, CHART_COLORS.orange, CHART_COLORS.red];
          return colors[i] + 'cc';
        }),
        borderRadius: 8,
        barPercentage: 0.55,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        tooltip: tooltipConfig(),
        legend: { display: false },
      },
      scales: {
        y: { title: { display: true, text: 'MIPS' }, beginAtZero: true },
      },
    },
  }, 'perfCompChart');

  animateCharts('perfCharts');
}

// ═══════════════════════════════════════════
//  PIPELINE SIMULATOR
// ═══════════════════════════════════════════

// Seeded PRNG (mulberry32)
function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6d2b79f5 | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function generateRandomStalls(numInstr, prob, seed) {
  const rng = mulberry32(seed);
  const stalls = [];
  for (let i = 0; i < numInstr - 1; i++) {
    if (rng() < prob) stalls.push(i);
  }
  return stalls;
}

function simulatePipeline() {
  const STAGES = ['IF', 'ID', 'EX', 'MEM', 'WB'];
  const numInstr = parseInt(document.getElementById('pipeNumInstr').value) || 6;
  let stallAfter = [];
  let stallCycles = 1;

  if (state.stallMode === 'manual') {
    const input = document.getElementById('stallAfterInput').value;
    stallAfter = [...new Set(
      input.split(',').map(s => parseInt(s.trim()) - 1).filter(n => !isNaN(n) && n >= 0 && n < numInstr - 1)
    )].sort((a, b) => a - b);
    stallCycles = parseInt(document.getElementById('stallCycles').value) || 1;
  } else if (state.stallMode === 'random') {
    const prob = parseFloat(document.getElementById('randProb').value) / 100;
    const seed = parseInt(document.getElementById('randSeed').value) || 42;
    stallCycles = parseInt(document.getElementById('stallCyclesRand').value) || 1;
    stallAfter = generateRandomStalls(numInstr, prob, seed);
  }

  // Build start-cycle array
  const startCycles = [];
  const stallSet = new Set(stallAfter);
  let currentStart = 0;
  for (let i = 0; i < numInstr; i++) {
    startCycles.push(currentStart);
    currentStart++;
    if (stallSet.has(i)) currentStart += stallCycles;
  }

  const totalCycles   = startCycles[numInstr - 1] + STAGES.length;
  const idealCycles   = numInstr + STAGES.length - 1;
  const noPipeCycles  = numInstr * STAGES.length;
  const totalStalls   = stallAfter.length * stallCycles;
  const cpi           = totalCycles / numInstr;
  const speedup       = noPipeCycles / totalCycles;
  const efficiency    = (idealCycles / totalCycles) * 100;

  // ── Stall alert ──
  const alertEl = document.getElementById('pipeStallAlert');
  if (stallAfter.length > 0) {
    const names = stallAfter.map(i => 'I' + (i + 1)).join(', ');
    alertEl.innerHTML = `<div class="alert alert-warning"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><span><strong>${totalStalls} stall cycle(s)</strong> inserted after: ${names}</span></div>`;
  } else {
    alertEl.innerHTML = `<div class="alert alert-success"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg><span>No stalls — ideal pipeline execution.</span></div>`;
  }

  // ── Metrics ──
  const metricsHTML = [
    { label: 'Total Cycles',    value: totalCycles,          accent: '' },
    { label: 'Ideal Cycles',    value: idealCycles,          accent: 'accent-green' },
    { label: 'Stall Cycles',    value: totalStalls,          accent: totalStalls > 0 ? 'accent-red' : '' },
    { label: 'CPI',             value: cpi.toFixed(2),       accent: 'accent-cyan' },
    { label: 'Speedup',         value: speedup.toFixed(2) + '\u00d7', accent: 'accent-purple' },
    { label: 'Efficiency',      value: efficiency.toFixed(1) + '%',   accent: 'accent-orange' },
  ].map(m => `<div class="metric-card ${m.accent}"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`).join('');

  document.getElementById('pipeMetrics').innerHTML = metricsHTML;
  animateResults('pipeResults');

  // ── Stage Legend ──
  const stageInfo = [
    { name: 'IF', cls: 'stage-if', color: '#3b82f6' },
    { name: 'ID', cls: 'stage-id', color: '#10b981' },
    { name: 'EX', cls: 'stage-ex', color: '#f59e0b' },
    { name: 'MEM', cls: 'stage-mem', color: '#8b5cf6' },
    { name: 'WB', cls: 'stage-wb', color: '#22d3ee' },
    { name: 'STALL', cls: '', color: '' },
  ];
  document.getElementById('stageLegend').innerHTML = stageInfo.map(s => {
    if (s.name === 'STALL') {
      return `<span class="legend-item"><span class="legend-dot" style="background:repeating-linear-gradient(45deg,rgba(239,68,68,.3),rgba(239,68,68,.3) 3px,transparent 3px,transparent 6px);border:1px dashed rgba(239,68,68,.5)"></span>Stall</span>`;
    }
    return `<span class="legend-item"><span class="legend-dot" style="background:${s.color}"></span>${s.name}</span>`;
  }).join('');

  // ── Gantt Grid ──
  renderGantt(numInstr, startCycles, stallAfter, stallCycles, STAGES, totalCycles);

  document.getElementById('pipeGanttCard').style.display = '';
  gsap.fromTo('#pipeGanttCard', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });
}

function renderGantt(numInstr, startCycles, stallAfter, stallCycles, stages, totalCycles) {
  const grid = document.getElementById('ganttGrid');
  grid.innerHTML = '';

  const stallSet = new Set(stallAfter);
  const cols = totalCycles + 1; // +1 for label column
  grid.style.gridTemplateColumns = `56px repeat(${totalCycles}, minmax(44px, 1fr))`;

  // Header row
  grid.appendChild(Object.assign(document.createElement('div'), { className: 'gantt-header', textContent: '' }));
  for (let c = 0; c < totalCycles; c++) {
    const h = document.createElement('div');
    h.className = 'gantt-header';
    h.textContent = 'C' + (c + 1);
    grid.appendChild(h);
  }

  // Instruction rows + stall rows
  for (let i = 0; i < numInstr; i++) {
    // Label
    const label = document.createElement('div');
    label.className = 'gantt-label';
    label.textContent = 'I' + (i + 1);
    grid.appendChild(label);

    // Cells
    for (let c = 0; c < totalCycles; c++) {
      const cell = document.createElement('div');
      cell.setAttribute('data-col', c);
      const stageIdx = c - startCycles[i];
      if (stageIdx >= 0 && stageIdx < stages.length) {
        const stageName = stages[stageIdx];
        cell.className = 'gantt-cell cell-' + stageName.toLowerCase();
        cell.textContent = stageName;
      } else {
        cell.className = 'gantt-cell cell-empty';
      }
      grid.appendChild(cell);
    }

    // Stall row after this instruction
    if (stallSet.has(i)) {
      for (let b = 0; b < stallCycles; b++) {
        const slabel = document.createElement('div');
        slabel.className = 'gantt-label stall-label';
        slabel.textContent = b === 0 ? '\u21b3 stall' : '';
        grid.appendChild(slabel);

        for (let c = 0; c < totalCycles; c++) {
          const cell = document.createElement('div');
          cell.setAttribute('data-col', c);
          const bubbleCycle = startCycles[i] + 1 + b;
          if (c === bubbleCycle) {
            cell.className = 'gantt-cell cell-stall';
            cell.textContent = 'bubble';
          } else {
            cell.className = 'gantt-cell cell-empty';
          }
          grid.appendChild(cell);
        }
      }
    }
  }

  // Animate gantt cells column-by-column
  for (let c = 0; c < totalCycles; c++) {
    const colCells = grid.querySelectorAll(`.gantt-cell[data-col="${c}"]:not(.cell-empty)`);
    gsap.fromTo(colCells,
      { opacity: 0, scale: 0.6, rotateY: -20 },
      { opacity: 1, scale: 1, rotateY: 0, duration: 0.35, stagger: 0.03, ease: 'back.out(1.5)', delay: 0.1 + c * 0.06 }
    );
  }
}

// ═══════════════════════════════════════════
//  CACHE ANALYZER
// ═══════════════════════════════════════════
function calculateAMAT() {
  if (state.cacheMode === 'single') {
    const hitTime  = parseFloat(document.getElementById('cacheHitTime').value) || 1;
    const missRate = parseFloat(document.getElementById('cacheMissRate').value) || 0.05;
    const missPen  = parseFloat(document.getElementById('cacheMissPen').value) || 100;
    const amat = hitTime + missRate * missPen;

    document.getElementById('cacheMetrics').innerHTML = [
      { label: 'Hit Time', value: hitTime.toFixed(2), accent: 'accent-green' },
      { label: 'Miss Rate', value: (missRate * 100).toFixed(1) + '%', accent: 'accent-orange' },
      { label: 'Miss Penalty', value: missPen.toFixed(1), accent: 'accent-red' },
      { label: 'AMAT', value: amat.toFixed(4) + ' cycles', accent: 'accent-cyan' },
    ].map(m => `<div class="metric-card ${m.accent}"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`).join('');

    animateResults('cacheResults');

    // Sensitivity chart
    const mrRange = [];
    const amatVals = [];
    for (let mr = 1; mr <= 50; mr++) {
      mrRange.push(mr / 100);
      amatVals.push(hitTime + (mr / 100) * missPen);
    }

    createChart('amatChart', {
      type: 'line',
      data: {
        labels: mrRange.map(v => (v * 100).toFixed(0) + '%'),
        datasets: [
          {
            label: 'AMAT',
            data: amatVals,
            borderColor: CHART_COLORS.primary,
            backgroundColor: CHART_COLORS.primary + '18',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2.5,
          },
          {
            label: 'Current (' + (missRate * 100).toFixed(0) + '%)',
            data: mrRange.map(() => amat),
            borderColor: CHART_COLORS.red,
            borderDash: [6, 4],
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { tooltip: tooltipConfig(), legend: { labels: { padding: 14 } } },
        scales: {
          x: { title: { display: true, text: 'Miss Rate' } },
          y: { title: { display: true, text: 'AMAT (cycles)' }, beginAtZero: true },
        },
      },
    }, 'amatChart');

    document.getElementById('cacheChartCard').style.display = '';
    gsap.fromTo('#cacheChartCard', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });

  } else {
    // Two-level
    const htL1 = parseFloat(document.getElementById('l1HitTime').value) || 1;
    const mrL1 = parseFloat(document.getElementById('l1MissRate').value) || 0.05;
    const htL2 = parseFloat(document.getElementById('l2HitTime').value) || 5;
    const mrL2 = parseFloat(document.getElementById('l2MissRate').value) || 0.10;
    const mpL2 = parseFloat(document.getElementById('l2MissPen').value) || 200;

    const amatL2 = htL2 + mrL2 * mpL2;
    const effectiveAMAT = htL1 + mrL1 * amatL2;

    document.getElementById('cacheMetrics').innerHTML = [
      { label: 'L1 Hit Time', value: htL1.toFixed(2), accent: '' },
      { label: 'L1 Miss Rate', value: (mrL1 * 100).toFixed(1) + '%', accent: 'accent-orange' },
      { label: 'L2 AMAT', value: amatL2.toFixed(4), accent: 'accent-purple' },
      { label: 'Effective AMAT', value: effectiveAMAT.toFixed(4), accent: 'accent-cyan' },
    ].map(m => `<div class="metric-card ${m.accent}"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`).join('');

    animateResults('cacheResults');

    // Comparison chart
    createChart('amatChart', {
      type: 'bar',
      data: {
        labels: ['L2-Only AMAT', 'Effective (L1+L2) AMAT'],
        datasets: [{
          data: [amatL2, effectiveAMAT],
          backgroundColor: [CHART_COLORS.purple + 'cc', CHART_COLORS.cyan + 'cc'],
          borderRadius: 8,
          barPercentage: 0.45,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false, indexAxis: 'y',
        plugins: { tooltip: tooltipConfig(), legend: { display: false } },
        scales: { x: { title: { display: true, text: 'AMAT (cycles)' }, beginAtZero: true } },
      },
    }, 'amatChart');

    document.getElementById('cacheChartCard').style.display = '';
    gsap.fromTo('#cacheChartCard', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });
  }
}

// ═══════════════════════════════════════════
//  AMDAHL'S LAW CALCULATOR
// ═══════════════════════════════════════════
function calculateAmdahl() {
  const parFrac = parseFloat(document.getElementById('amdParFrac').value) / 100;
  const S = parseFloat(document.getElementById('amdSpeedupS').value) || 8;
  const maxProc = parseInt(document.getElementById('amdMaxProc').value) || 64;

  const serialFrac = 1 - parFrac;
  const speedup = serialFrac > 0 ? 1 / (serialFrac + parFrac / S) : S;
  const maxSpeedup = parFrac < 1 ? 1 / serialFrac : Infinity;

  // Metrics
  document.getElementById('amdMetrics').innerHTML = [
    { label: 'Parallel Fraction', value: (parFrac * 100).toFixed(0) + '%', accent: '' },
    { label: 'Enhanced Speedup (S)', value: S.toFixed(1) + '\u00d7', accent: 'accent-cyan' },
    { label: 'Overall Speedup', value: speedup.toFixed(4) + '\u00d7', accent: 'accent-green' },
    { label: 'Max Speedup (S\u2192\u221e)', value: maxSpeedup === Infinity ? '\u221e' : maxSpeedup.toFixed(4) + '\u00d7', accent: 'accent-purple' },
  ].map(m => `<div class="metric-card ${m.accent}"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`).join('');

  animateResults('amdResults');

  // Speedup curve
  const processors = [];
  const speedups = [];
  for (let p = 1; p <= maxProc; p++) {
    processors.push(p);
    speedups.push(1 / (serialFrac + parFrac / p));
  }

  createChart('amdahlChart', {
    type: 'line',
    data: {
      labels: processors,
      datasets: [
        {
          label: 'Speedup',
          data: speedups,
          borderColor: CHART_COLORS.primary,
          backgroundColor: CHART_COLORS.primary + '15',
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 5,
          borderWidth: 2.5,
        },
        {
          label: 'Max (' + (maxSpeedup === Infinity ? '\u221e' : maxSpeedup.toFixed(2)) + ')',
          data: processors.map(() => maxSpeedup === Infinity ? null : maxSpeedup),
          borderColor: CHART_COLORS.red,
          borderDash: [8, 4],
          borderWidth: 2,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { tooltip: tooltipConfig(), legend: { labels: { padding: 14 } } },
      scales: {
        x: { title: { display: true, text: 'Number of Processors (S)' } },
        y: { title: { display: true, text: 'Overall Speedup' }, beginAtZero: true },
      },
    },
  }, 'amdahlChart');

  document.getElementById('amdChartCard').style.display = '';
  gsap.fromTo('#amdChartCard', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });

  // Comparison table
  const pValues = [0.50, 0.75, 0.90, 0.95, 0.99];
  const tbody = document.querySelector('#amdCompTable tbody');
  tbody.innerHTML = pValues.map(p => {
    const maxSp = p < 1 ? (1 / (1 - p)).toFixed(2) : '\u221e';
    const spAtS = (1 / ((1 - p) + p / S)).toFixed(4);
    const highlight = Math.abs(p - parFrac) < 0.005 ? ' style="color:var(--primary-light);font-weight:700"' : '';
    return `<tr${highlight}><td>${(p * 100).toFixed(0)}%</td><td>${maxSp}\u00d7</td><td>${spAtS}\u00d7</td></tr>`;
  }).join('');

  document.getElementById('amdTableCard').style.display = '';
  gsap.fromTo('#amdTableCard', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out', delay: 0.15 });
}
