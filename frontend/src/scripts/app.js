// Full STRINGS for EN and ES
const STRINGS = {
  en: {
    hero: {
      badge: 'Free · open source · Tkinter desktop app',
      title: 'Sort your photos by the day they were taken.',
      tagline: 'A desktop app that reads each photo’s date and copies it into a tidy Year / Month folder tree. Your originals are never moved or deleted.',
      primaryCta: 'Download for {os}',
      otherCta: 'All platforms',
      meta: 'Free & open source · macOS, Windows & Linux',
    },
    visual: {
      title: 'Output folder',
      before: 'Unsorted input',
      arrow: 'sorted by capture date',
      jun: '06-June',
      jul: '07-July',
      dec: '12-December',
    },
    promise: {
      title: 'Your originals never move.',
      sub: 'Photos Sorter only ever copies. Nothing in your source folder is renamed, moved, or deleted — ever. No other data on your system is touched.',
    },
    feat: {
      eyebrow: 'Features',
      title: 'Everything it does for your library',
      lead: 'Smart about dates, careful with your files.',
      f1: { title: 'Smart date detection', desc: 'Reads EXIF capture dates, Google Takeout sidecars and filesystem timestamps — in priority order — so every file lands on the right day.' },
      f2: { title: 'Tidy folder trees', desc: 'Organises everything into Year / Month folders. Choose plain numbers (2024/06) or named months (2024/06-June).' },
      f3: { title: 'Google Takeout ready', desc: 'Turn on Takeout mode and it reads photoTakenTime from each sidecar JSON. The JSON files are never copied across.' },
      f4: { title: 'Every common format', desc: 'JPEG, PNG, HEIC/HEIF, MOV and MP4. Input folders are scanned recursively, however deep they go.' },
      f5: { title: 'No overwrites, ever', desc: 'Duplicate names are auto-renamed — IMG_001.jpg becomes IMG_001 (1).jpg. Nothing is lost.' },
      f6: { title: 'Bilingual & remembered', desc: 'Full English and Spanish UI with localised month names, and your settings saved between runs.' },
    },
    how: {
      eyebrow: 'How it works',
      title: 'Three steps to a sorted library',
      steps: [
        { n: '01', title: 'Pick a folder', desc: 'Point Photos Sorter at any folder of photos and videos — nested subfolders included.' },
        { n: '02', title: 'Choose your options', desc: 'Month format, language and Google Takeout mode. Set them once — they’re remembered.' },
        { n: '03', title: 'Get a sorted copy', desc: 'A clean Year / Month tree appears in your output folder. Originals stay exactly where they are.' },
      ],
    },
    caveats: {
      eyebrow: 'Good to know',
      title: 'When a file might land in the wrong place',
      c1: { title: 'Videos use file dates', desc: 'Videos (.mov, .mp4) don\'t have their embedded capture date read — they\'re sorted by file-system timestamps (or a Google Takeout date, if present). If those were altered, a video can land in the wrong month.' },
      c2: { title: 'Photos with stripped metadata', desc: 'Screenshots, edited exports, and images received via apps like WhatsApp often lose their EXIF data and fall back to file dates — usually when you downloaded the file, not when it was taken.' },
      c3: { title: 'Unsupported formats are skipped', desc: 'Only JPEG, PNG, HEIC/HEIF, MOV and MP4 are processed. RAW (CR2, NEF, DNG), TIFF, GIF, WebP, AVI, MKV and others are skipped and left untouched.' },
      c4: { title: 'No date? Nothing is lost', desc: 'If no capture date and no file date can be read at all, the file is copied into an "Unknown" folder so nothing is lost — you can sort those by hand.' },
    },
    dl: {
      eyebrow: 'Download',
      title: 'Get Photos Sorter',
      lead: 'Free and open source. Grab a build for your system, or run it from source.',
      btn: 'Download',
      mac: 'macOS 11+ · .app bundle',
      win: 'Windows 10 / 11 · .exe',
      linux: 'Standalone binary',
      buildTitle: 'Or build from source',
      buildLead: 'Requires Python 3.13+ and the uv package manager.',
      buildInstaller: 'Build the installer (choose your OS — macos, windows, linux):',
    },
    install: {
      title: 'First launch — your system may block it',
      intro: 'These builds are unsigned, so your OS shows a one-time security warning. Here\'s how to allow Photos Sorter on each system.',
      mac: 'macOS says the app is from an unidentified developer and can\'t be checked for malware. After moving Photos Sorter to your Applications folder, run this once in Terminal, then open it normally:',
      win: 'Windows SmartScreen warns that the publisher is unknown. Click "More info" on the dialog, then "Run anyway".',
      linux: 'Make the AppImage executable, then run it:',
    },
    ui: { copy: 'Copy', copied: 'Copied!' },
    footer: { rights: '© 2026 · Built with Python & Tkinter', releases: 'Releases' },
  },
  es: {
    hero: {
      badge: 'Gratis · código abierto · app de escritorio',
      title: 'Ordena tus fotos por el día en que se tomaron.',
      tagline: 'Una app de escritorio que lee la fecha de cada foto y la copia en un árbol ordenado de carpetas Año / Mes. Tus originales nunca se mueven ni se eliminan.',
      primaryCta: 'Descargar para {os}',
      otherCta: 'Todas las plataformas',
      meta: 'Gratis y de código abierto · macOS, Windows y Linux',
    },
    visual: {
      title: 'Carpeta de salida',
      before: 'Entrada sin ordenar',
      arrow: 'ordenado por fecha de captura',
      jun: '06-Junio',
      jul: '07-Julio',
      dec: '12-Diciembre',
    },
    promise: {
      title: 'Tus originales nunca se mueven.',
      sub: 'Photos Sorter solo copia. Nada en tu carpeta de origen se renombra, se mueve ni se elimina, nunca. Ningún otro dato de tu sistema se ve afectado.',
    },
    feat: {
      eyebrow: 'Funciones',
      title: 'Todo lo que hace por tu biblioteca',
      lead: 'Inteligente con las fechas, cuidadoso con tus archivos.',
      f1: { title: 'Detección inteligente de fechas', desc: 'Lee las fechas EXIF, los JSON de Google Takeout y las marcas de tiempo del sistema —por orden de prioridad— para que cada archivo caiga en el día correcto.' },
      f2: { title: 'Árboles de carpetas ordenados', desc: 'Organiza todo en carpetas Año / Mes. Elige números (2024/06) o meses con nombre (2024/06-Junio).' },
      f3: { title: 'Compatible con Google Takeout', desc: 'Activa el modo Takeout y leerá photoTakenTime de cada archivo JSON. Los JSON nunca se copian.' },
      f4: { title: 'Todos los formatos habituales', desc: 'JPEG, PNG, HEIC/HEIF, MOV y MP4. Las carpetas se analizan de forma recursiva, por muy profundas que sean.' },
      f5: { title: 'Sin sobrescrituras, nunca', desc: 'Los nombres duplicados se renombran solos: IMG_001.jpg pasa a IMG_001 (1).jpg. No se pierde nada.' },
      f6: { title: 'Bilingüe y con memoria', desc: 'Interfaz completa en inglés y español con meses localizados, y tus ajustes guardados entre sesiones.' },
    },
    how: {
      eyebrow: 'Cómo funciona',
      title: 'Tres pasos hacia una biblioteca ordenada',
      steps: [
        { n: '01', title: 'Elige una carpeta', desc: 'Indica a Photos Sorter cualquier carpeta de fotos y vídeos, incluidas las subcarpetas.' },
        { n: '02', title: 'Elige tus opciones', desc: 'Formato de mes, idioma y modo Google Takeout. Confíguralo una vez: se recuerda.' },
        { n: '03', title: 'Obtén una copia ordenada', desc: 'Aparece un árbol Año / Mes limpio en tu carpeta de salida. Los originales se quedan donde están.' },
      ],
    },
    caveats: {
      eyebrow: 'Ten en cuenta',
      title: 'Cuándo un archivo puede acabar en el lugar equivocado',
      c1: { title: 'Los vídeos usan la fecha del archivo', desc: 'Los vídeos (.mov, .mp4) no se ordenan por su fecha de captura incrustada, sino por las marcas de tiempo del sistema de archivos (o la fecha de Google Takeout, si existe). Si se han modificado, un vídeo puede acabar en el mes equivocado.' },
      c2: { title: 'Fotos sin metadatos', desc: 'Las capturas de pantalla, exportaciones editadas e imágenes recibidas por apps como WhatsApp suelen perder sus datos EXIF y usan la fecha del archivo, normalmente la de descarga y no la de captura.' },
      c3: { title: 'Los formatos no compatibles se omiten', desc: 'Solo se procesan JPEG, PNG, HEIC/HEIF, MOV y MP4. RAW (CR2, NEF, DNG), TIFF, GIF, WebP, AVI, MKV y otros se omiten y permanecen intactos.' },
      c4: { title: '¿Sin fecha? No se pierde nada', desc: 'Si no se puede leer ninguna fecha de captura ni de archivo, el archivo se copia en una carpeta "Unknown" para no perder nada; esos los ordenas a mano.' },
    },
    dl: {
      eyebrow: 'Descargar',
      title: 'Consigue Photos Sorter',
      lead: 'Gratis y de código abierto. Descarga una versión para tu sistema o ejécutalo desde el código.',
      btn: 'Descargar',
      mac: 'macOS 11+ · paquete .app',
      win: 'Windows 10 / 11 · .exe',
      linux: 'Binario independiente',
      buildTitle: 'O compílalo desde el código',
      buildLead: 'Requiere Python 3.13+ y el gestor de paquetes uv.',
      buildInstaller: 'Compila el instalador (elige tu SO — macos, windows, linux):',
    },
    install: {
      title: 'Primer inicio — tu sistema puede bloquearlo',
      intro: 'Estas versiones no están firmadas, así que tu sistema muestra un aviso de seguridad la primera vez. Así puedes permitir Photos Sorter en cada sistema.',
      mac: 'macOS dice que la app es de un desarrollador no identificado y que no puede comprobar si tiene malware. Tras mover Photos Sorter a tu carpeta de Aplicaciones, ejecuta esto una vez en la Terminal y luego ábrela normalmente:',
      win: 'Windows SmartScreen avisa de que el editor es desconocido. Haz clic en "Más información" en el aviso y luego en "Ejecutar de todas formas".',
      linux: 'Haz el AppImage ejecutable y luego ejecútalo:',
    },
    ui: { copy: 'Copiar', copied: '¡Copiado!' },
    footer: { rights: '© 2026 · Hecho con Python y Tkinter', releases: 'Versiones' },
  },
};

// Download URLs per OS
const DOWNLOAD_URLS = {
  mac: 'https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-macos.dmg',
  win: 'https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-windows.exe',
  linux: 'https://github.com/oscaroteromar/photos_sorter/releases/latest/download/Photos-Sorter-linux.AppImage',
};

function detectOS() {
  const ua = (navigator.userAgent || '') + ' ' + (navigator.platform || '');
  if (/Mac/i.test(ua)) return 'mac';
  if (/Win/i.test(ua)) return 'win';
  if (/Linux|X11|Android/i.test(ua)) return 'linux';
  return 'mac';
}

// --- State ---
let currentLang = 'es';
let currentTheme = 'light';
let langBusy = false;

function initState() {
  try {
    currentTheme = localStorage.getItem('ps_theme') || currentTheme;
    currentLang = localStorage.getItem('ps_lang') || currentLang;
  } catch (e) {}

  // Theme: auto-detect from OS preference when no stored value
  if (!localStorage.getItem('ps_theme')) {
    currentTheme = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  }
  // Language: default is Spanish; a stored preference always wins (set above)

  applyTheme(currentTheme);
  applyLang(currentLang);

  // Enable color transitions after first paint to avoid FOUC
  setTimeout(() => {
    try { document.documentElement.setAttribute('data-anim', ''); } catch (e) {}
  }, 60);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

function setTheme(theme) {
  currentTheme = theme;
  applyTheme(theme);
  try { localStorage.setItem('ps_theme', theme); } catch (e) {}
  updateThemeButton();
}

function toggleTheme() {
  setTheme(currentTheme === 'dark' ? 'light' : 'dark');
}

function updateThemeButton() {
  const btn = document.getElementById('ps-theme-btn');
  if (!btn) return;
  const isDark = currentTheme === 'dark';
  btn.innerHTML = isDark
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.2 4.2l1.5 1.5M18.3 18.3l1.5 1.5M2 12h2M20 12h2M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"/></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 1 1 9.5 4 6.5 6.5 0 0 0 20 14.5z"/></svg>`;
}

function setLang(lang) {
  if (lang === currentLang || langBusy) return;
  try { localStorage.setItem('ps_lang', lang); } catch (e) {}
  const el = document.getElementById('ps-main');
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!el || reduce) {
    currentLang = lang;
    applyLang(lang);
    return;
  }
  langBusy = true;
  el.style.opacity = '0';
  setTimeout(() => {
    currentLang = lang;
    applyLang(lang);
    setTimeout(() => {
      const e2 = document.getElementById('ps-main');
      if (e2) e2.style.opacity = '1';
      langBusy = false;
    }, 40);
  }, 230);
}

function applyLang(lang) {
  const S = STRINGS[lang] || STRINGS.en;
  const os = detectOS();
  const osLabel = { mac: 'macOS', win: 'Windows', linux: 'Linux' }[os];
  const downloadUrl = DOWNLOAD_URLS[os];

  // Update all data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = getNestedKey(S, key);
    if (val !== undefined) el.textContent = val;
  });

  // Primary CTA label
  const primaryLabel = S.hero.primaryCta.replace('{os}', osLabel);
  document.querySelectorAll('[data-i18n-primary-label]').forEach(el => {
    el.textContent = primaryLabel;
  });

  // Update per-OS download hrefs
  document.querySelectorAll('[data-download-os]').forEach(el => {
    const dlOs = el.getAttribute('data-download-os');
    el.href = DOWNLOAD_URLS[dlOs] || DOWNLOAD_URLS.mac;
  });

  // Hero primary CTA href (detected OS)
  document.querySelectorAll('[data-download-primary]').forEach(el => {
    el.href = downloadUrl;
  });

  // How-it-works steps
  const steps = S.how.steps;
  document.querySelectorAll('[data-step]').forEach(el => {
    const idx = parseInt(el.getAttribute('data-step'), 10);
    const step = steps[idx];
    if (!step) return;
    const nEl = el.querySelector('[data-step-n]');
    const titleEl = el.querySelector('[data-step-title]');
    const descEl = el.querySelector('[data-step-desc]');
    if (nEl) nEl.textContent = step.n;
    if (titleEl) titleEl.textContent = step.title;
    if (descEl) descEl.textContent = step.desc;
  });

  // Build installer label (i18n only; make command is OS-static and set once in updateMakeCommand)
  const buildInstallerEl = document.getElementById('ps-build-installer-label');
  if (buildInstallerEl) buildInstallerEl.textContent = S.dl.buildInstaller;

  // Language segmented control styling
  updateSegButtons(lang);
  // Theme button
  updateThemeButton();

  // Update html lang attribute
  document.documentElement.lang = lang;
}

function getNestedKey(obj, path) {
  return path.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), obj);
}

function updateSegButtons(lang) {
  const enBtn = document.getElementById('ps-lang-en');
  const esBtn = document.getElementById('ps-lang-es');
  if (!enBtn || !esBtn) return;
  const activeStyle = 'background:var(--inv);color:var(--invInk);';
  const inactiveStyle = 'background:transparent;color:var(--muted);';
  enBtn.setAttribute('style', enBtn.getAttribute('data-base-style') + (lang === 'en' ? activeStyle : inactiveStyle));
  esBtn.setAttribute('style', esBtn.getAttribute('data-base-style') + (lang === 'es' ? activeStyle : inactiveStyle));
}

function updateMakeCommand() {
  const os = detectOS();
  const makeTarget = { mac: 'macos', win: 'windows', linux: 'linux' }[os];
  const el = document.getElementById('ps-build-make-cmd');
  if (el) el.textContent = '$ cd app && make ' + makeTarget;
}

// --- Copy-to-clipboard helpers ---

const CLIPBOARD_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
const CHECK_ICON = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>`;

function makeCopyButton() {
  const btn = document.createElement('button');
  btn.className = 'ps-copy-btn';
  btn.setAttribute('aria-label', STRINGS[currentLang].ui.copy);
  btn.innerHTML = CLIPBOARD_ICON;
  return btn;
}

function attachCopyHandler(btn, getTextFn) {
  btn.addEventListener('click', async () => {
    const S = STRINGS[currentLang] || STRINGS.en;
    const text = getTextFn();
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      btn.innerHTML = CHECK_ICON;
      btn.setAttribute('aria-label', S.ui.copied);
      setTimeout(() => {
        btn.innerHTML = CLIPBOARD_ICON;
        btn.setAttribute('aria-label', (STRINGS[currentLang] || STRINGS.en).ui.copy);
      }, 1500);
    } catch (err) {
      // Silently fail — do not throw unhandled errors
    }
  });
}

function initCopyButtons() {
  // 1. Build-from-source box
  const buildBox = document.getElementById('ps-build-make-cmd');
  if (buildBox) {
    const wrapper = buildBox.parentElement;
    wrapper.style.position = 'relative';
    const btn = makeCopyButton();
    wrapper.appendChild(btn);
    attachCopyHandler(btn, () => {
      const raw = (document.getElementById('ps-build-make-cmd') || buildBox).textContent || '';
      // Strip leading "$ " prompt
      return raw.replace(/^\$\s*/, '');
    });
  }

  // 2. macOS install box
  const macBox = document.getElementById('ps-install-mac-cmd');
  if (macBox) {
    macBox.style.position = 'relative';
    const btn = makeCopyButton();
    macBox.appendChild(btn);
    attachCopyHandler(btn, () => 'xattr -dr com.apple.quarantine "/Applications/Photos Sorter.app"');
  }

  // 3. Linux install box
  const linuxBox = document.getElementById('ps-install-linux-cmd');
  if (linuxBox) {
    linuxBox.style.position = 'relative';
    const btn = makeCopyButton();
    linuxBox.appendChild(btn);
    attachCopyHandler(btn, () => 'chmod +x Photos-Sorter-linux.AppImage\n./Photos-Sorter-linux.AppImage');
  }
}

// Wire up event listeners after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initState();
  updateMakeCommand();

  const enBtn = document.getElementById('ps-lang-en');
  const esBtn = document.getElementById('ps-lang-es');
  const themeBtn = document.getElementById('ps-theme-btn');

  if (enBtn) enBtn.addEventListener('click', () => setLang('en'));
  if (esBtn) esBtn.addEventListener('click', () => setLang('es'));
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  initCopyButtons();
});
