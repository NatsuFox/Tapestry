const root = document.documentElement;
const navToggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".site-nav");

root.classList.add("js");

const resolvePath = (obj, path) =>
  path.split(".").reduce((current, key) => {
    if (current === undefined || current === null) {
      return undefined;
    }
    return current[key];
  }, obj);

const formatTemplate = (template, params = {}) =>
  String(template).replace(/\{(\w+)\}/g, (_, key) => {
    if (params[key] === undefined || params[key] === null) {
      return `{${key}}`;
    }
    return String(params[key]);
  });

const applyLexicon = (lexicon) => {
  document.querySelectorAll("[data-copy]").forEach((element) => {
    const value = resolvePath(lexicon, element.dataset.copy);
    if (value !== undefined) {
      element.textContent = String(value);
    }
  });

  document.querySelectorAll("[data-copy-alt]").forEach((element) => {
    const value = resolvePath(lexicon, element.dataset.copyAlt);
    if (value !== undefined) {
      element.setAttribute("alt", String(value));
    }
  });

  document.querySelectorAll("[data-copy-content]").forEach((element) => {
    const value = resolvePath(lexicon, element.dataset.copyContent);
    if (value !== undefined) {
      element.setAttribute("content", String(value));
    }
  });

  document.querySelectorAll("[data-copy-aria-label]").forEach((element) => {
    const value = resolvePath(lexicon, element.dataset.copyAriaLabel);
    if (value !== undefined) {
      element.setAttribute("aria-label", String(value));
    }
  });

  document.querySelectorAll("[data-structure-key]").forEach((node) => {
    const key = node.dataset.structureKey;
    const data = resolvePath(lexicon, `overview.structure.nodes.${key}`);
    if (!data) {
      return;
    }
    node.dataset.title = data.label.cn;
    node.dataset.english = data.label.en;
    node.dataset.detail = data.detail;
  });

  document.querySelectorAll("[data-preview-key]").forEach((slide) => {
    const key = slide.dataset.previewKey;
    const data = resolvePath(lexicon, `preview.slides.${key}`);
    if (!data) {
      return;
    }
    slide.dataset.title = data.title;
    slide.dataset.caption = data.caption;
  });
};

const initNav = () => {
  if (!navToggle || !nav) {
    return;
  }

  navToggle.addEventListener("click", () => {
    const isOpen = root.classList.toggle("nav-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      root.classList.remove("nav-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
};

const initLogoMotion = () => {
  const motionContainer = document.querySelector("[data-logo-motion]");
  const heroWordmark = document.querySelector(".hero-wordmark");

  if (!motionContainer || !heroWordmark || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  const resetLogoMotion = () => {
    motionContainer.style.setProperty("--logo-tilt-x", "0deg");
    motionContainer.style.setProperty("--logo-tilt-y", "0deg");
    motionContainer.style.setProperty("--logo-shift-x", "0px");
    motionContainer.style.setProperty("--logo-shift-y", "0px");
  };

  motionContainer.addEventListener("pointermove", (event) => {
    const rect = motionContainer.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width - 0.5;
    const py = (event.clientY - rect.top) / rect.height - 0.5;
    motionContainer.style.setProperty("--logo-tilt-x", `${(-py * 5).toFixed(2)}deg`);
    motionContainer.style.setProperty("--logo-tilt-y", `${(px * 7).toFixed(2)}deg`);
    motionContainer.style.setProperty("--logo-shift-x", `${(px * 10).toFixed(2)}px`);
    motionContainer.style.setProperty("--logo-shift-y", `${(py * 8).toFixed(2)}px`);
  });

  motionContainer.addEventListener("pointerleave", resetLogoMotion);
  resetLogoMotion();
};

const initStructure = () => {
  const structure = document.querySelector("[data-structure]");

  if (!structure) {
    return;
  }

  const nodes = Array.from(structure.querySelectorAll(".structure-node-group"));
  const titleEl = structure.querySelector("[data-structure-title]");
  const detailEl = structure.querySelector("[data-structure-detail]");
  const englishEl = structure.querySelector("[data-structure-english]");

  const activateNode = (node) => {
    nodes.forEach((item) => item.classList.toggle("is-active", item === node));
    if (titleEl) {
      titleEl.textContent = node.dataset.title || "";
    }
    if (detailEl) {
      detailEl.textContent = node.dataset.detail || "";
    }
    if (englishEl) {
      englishEl.textContent = node.dataset.english || "";
    }
  };

  nodes.forEach((node) => {
    ["mouseenter", "click"].forEach((eventName) => {
      node.addEventListener(eventName, () => activateNode(node));
    });
  });

  if (nodes[0]) {
    activateNode(nodes[0]);
  }
};

const initTerminal = () => {
  const terminalPlayer = document.querySelector("[data-cast-player]");

  if (terminalPlayer && window.AsciinemaPlayer) {
    window.AsciinemaPlayer.create(terminalPlayer.dataset.castSrc, terminalPlayer, {
      autoPlay: true,
      loop: true,
      controls: true,
      preload: true,
      fit: "width",
      theme: "asciinema"
    });
  }
};

const initPreview = (lexicon) => {
  const preview = document.querySelector("[data-preview]");

  if (!preview) {
    return;
  }

  const track = preview.querySelector("[data-preview-track]");
  const slides = Array.from(preview.querySelectorAll(".preview-slide"));
  const dotsRoot = preview.querySelector("[data-preview-dots]");
  const prevButton = preview.querySelector("[data-preview-prev]");
  const nextButton = preview.querySelector("[data-preview-next]");
  const titleEl = preview.querySelector("[data-preview-title]");
  const captionEl = preview.querySelector("[data-preview-caption]");
  const timerBar = preview.querySelector("[data-preview-timer]");
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dotAriaTemplate =
    resolvePath(lexicon, "preview.controls.dotAriaLabelTemplate") || "跳转到第 {n} 张预览";

  let currentIndex = 0;
  let autoplayId = null;
  const intervalMs = 5200;

  const dots = slides.map((_, index) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = "preview-dot";
    dot.setAttribute("aria-label", formatTemplate(dotAriaTemplate, { n: index + 1 }));
    dot.addEventListener("click", () => {
      setSlide(index);
      startAutoplay();
    });
    dotsRoot?.append(dot);
    return dot;
  });

  const restartTimer = () => {
    if (!timerBar || prefersReducedMotion || slides.length < 2) {
      return;
    }

    timerBar.classList.remove("is-running");
    timerBar.style.animationPlayState = "running";
    timerBar.style.setProperty("--preview-duration", `${intervalMs}ms`);
    void timerBar.offsetWidth;
    timerBar.classList.add("is-running");
  };

  const pauseTimer = () => {
    if (timerBar) {
      timerBar.style.animationPlayState = "paused";
    }
  };

  const setSlide = (index) => {
    if (!track || slides.length === 0) {
      return;
    }

    currentIndex = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${currentIndex * 100}%)`;

    dots.forEach((dot, dotIndex) => {
      dot.classList.toggle("is-active", dotIndex === currentIndex);
    });

    const currentSlide = slides[currentIndex];
    if (titleEl) {
      titleEl.textContent = currentSlide.dataset.title || "";
    }
    if (captionEl) {
      captionEl.textContent = currentSlide.dataset.caption || "";
    }

    restartTimer();
  };

  const stopAutoplay = () => {
    if (autoplayId) {
      window.clearInterval(autoplayId);
      autoplayId = null;
    }
    pauseTimer();
  };

  const startAutoplay = () => {
    if (prefersReducedMotion || slides.length < 2) {
      return;
    }
    if (autoplayId) {
      window.clearInterval(autoplayId);
    }
    restartTimer();
    autoplayId = window.setInterval(() => {
      setSlide(currentIndex + 1);
    }, intervalMs);
  };

  prevButton?.addEventListener("click", () => {
    setSlide(currentIndex - 1);
    startAutoplay();
  });

  nextButton?.addEventListener("click", () => {
    setSlide(currentIndex + 1);
    startAutoplay();
  });

  preview.addEventListener("mouseenter", stopAutoplay);
  preview.addEventListener("mouseleave", startAutoplay);
  preview.addEventListener("focusin", stopAutoplay);
  preview.addEventListener("focusout", startAutoplay);

  setSlide(0);
  startAutoplay();
};

const bootstrap = async () => {
  let lexicon = null;
  try {
    const response = await fetch("./lexicon.json", { cache: "no-store" });
    if (response.ok) {
      lexicon = await response.json();
      applyLexicon(lexicon);
    }
  } catch (error) {
    console.warn("Failed to load portal lexicon:", error);
  }

  initNav();
  initLogoMotion();
  initStructure();
  initTerminal();
  initPreview(lexicon);
};

bootstrap();
