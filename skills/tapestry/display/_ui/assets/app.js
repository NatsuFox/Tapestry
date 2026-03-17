const state = {
  manifest: null,
  documents: {},
  nodes: new Map(),
  activePath: null,
  query: "",
  expanded: new Set(["."]),
  langPreference: "auto",
  uiLang: "en",
};

// DOM elements - will be initialized after DOM is ready
let treeEl, searchEl, searchResultsEl, titleEl, subtitleEl, heroStatsEl;
let bodyEl, relatedSectionEl, tocEl, metaEl, siblingLinksEl, breadcrumbsEl;
let navToggleEl, sidebarEl, sidebarBackdropEl, homeLinkEl;
let themeSelectEl, langSelectEl;

const translations = {
  en: {
    "knowledge-base": "Knowledge Base",
    "tagline": "Browse topics, chapters, and evolving research notes in one readable surface.",
    "theme": "Theme",
    "language": "Language / 语言",
    "open-root": "Open Root Index",
    "search-label": "Find a topic or document",
    "search-placeholder": "Search titles, paths, excerpts",
    "search-button": "Search",
    "word-count": "Word Count",
    "headings": "Headings",
    "section-depth": "Section Depth",
    "sibling-docs": "Sibling Docs",
    "kind": "Kind",
    "path": "Path",
    "updated": "Updated",
    "unknown": "unknown",
    "document-meta": "Document Meta",
    "on-this-page": "On This Page",
    "nearby": "Nearby",
    "continue-exploring": "Continue Exploring",
    "no-headings": "No section headings detected.",
    "no-nearby": "No nearby sections available.",
    "no-related": "No related documents found in this section.",
    "chapter-homepage": "Chapter Homepage",
  },
  zh: {
    "knowledge-base": "知识库",
    "tagline": "浏览主题、章节和不断演进的研究笔记。",
    "theme": "主题",
    "language": "语言 / Language",
    "open-root": "打开根目录",
    "search-label": "查找主题或文档",
    "search-placeholder": "搜索标题、路径、摘要",
    "search-button": "搜索",
    "word-count": "字数",
    "headings": "标题数",
    "section-depth": "章节深度",
    "sibling-docs": "同级文档",
    "kind": "类型",
    "path": "路径",
    "updated": "更新时间",
    "unknown": "未知",
    "document-meta": "文档信息",
    "on-this-page": "本页目录",
    "nearby": "相关章节",
    "continue-exploring": "继续探索",
    "no-headings": "未检测到章节标题。",
    "no-nearby": "没有相关章节。",
    "no-related": "本节没有相关文档。",
    "chapter-homepage": "章节主页",
  },
};

function updateUILanguage(lang) {
  state.uiLang = lang;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (translations[lang] && translations[lang][key]) {
      el.placeholder = translations[lang][key];
    }
  });
}

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('Initializing Tapestry viewer...');

  // Initialize DOM element references
  treeEl = document.getElementById("tree");
  searchEl = document.getElementById("search");
  searchResultsEl = document.getElementById("search-results");
  titleEl = document.getElementById("page-title");
  subtitleEl = document.getElementById("page-subtitle");
  heroStatsEl = document.getElementById("hero-stats");
  bodyEl = document.getElementById("content-body");
  relatedSectionEl = document.getElementById("related-section");
  tocEl = document.getElementById("toc");
  metaEl = document.getElementById("doc-meta");
  siblingLinksEl = document.getElementById("sibling-links");
  breadcrumbsEl = document.getElementById("breadcrumbs");
  navToggleEl = document.getElementById("nav-toggle");
  sidebarEl = document.getElementById("sidebar");
  sidebarBackdropEl = document.getElementById("sidebar-backdrop");
  homeLinkEl = document.getElementById("home-link");
  themeSelectEl = document.getElementById("theme-select");
  langSelectEl = document.getElementById("lang-select");

  console.log('Elements found:', {
    navToggle: !!navToggleEl,
    sidebar: !!sidebarEl,
    backdrop: !!sidebarBackdropEl,
    search: !!searchEl
  });

  // Load saved theme
  const savedTheme = localStorage.getItem("tapestry-theme") || "default";
  if (savedTheme !== "default") {
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeSelectEl.value = savedTheme;
  }

  themeSelectEl.addEventListener("change", () => {
    const theme = themeSelectEl.value;
    if (theme === "default") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", theme);
    }
    localStorage.setItem("tapestry-theme", theme);
  });

  // Load saved language preference
  const savedLang = localStorage.getItem("tapestry-lang") || "auto";
  langSelectEl.value = savedLang;
  state.langPreference = savedLang;

  // Initialize UI language
  const initialUILang = savedLang === "zh" ? "zh" : "en";
  updateUILanguage(initialUILang);

  langSelectEl.addEventListener("change", () => {
    const lang = langSelectEl.value;
    state.langPreference = lang;
    localStorage.setItem("tapestry-lang", lang);

    // Update UI language
    const uiLang = lang === "zh" ? "zh" : "en";
    updateUILanguage(uiLang);

    // Refresh current document to apply language preference
    if (state.activePath) {
      openDoc(state.activePath);
    }
  });

function escapeHtml(text = "") {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function detectLanguage(text) {
  const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
  const totalChars = text.replace(/\s/g, "").length;
  return chineseChars / totalChars > 0.3 ? "zh" : "en";
}

function inlineMarkdown(text = "", currentPath = "") {
  let rendered = escapeHtml(text);

  // Handle markdown links first (before other formatting to avoid conflicts)
  rendered = rendered.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const resolved = resolveLink(currentPath, href);
    if (resolved.internal) {
      return `<a href="#/${resolved.path}" data-doc-link="${resolved.path}">${label}</a>`;
    }
    return `<a href="${href}" target="_blank" rel="noreferrer noopener">${label}</a>`;
  });

  // Auto-link plain URLs (http:// or https://)
  rendered = rendered.replace(/(?<!href="|">)(https?:\/\/[^\s<>()\[\]{}]+)/g, (url) => {
    // Remove trailing punctuation that's likely not part of the URL
    const cleanUrl = url.replace(/[.,;:!?)\]]+$/, '');
    const trailing = url.slice(cleanUrl.length);
    return `<a href="${cleanUrl}" target="_blank" rel="noreferrer noopener">${cleanUrl}</a>${trailing}`;
  });

  // Handle inline code (before bold/italic to avoid conflicts)
  rendered = rendered.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Handle bold and italic
  rendered = rendered.replace(/\*\*\*([^*]+)\*\*\*/g, "<strong><em>$1</em></strong>");
  rendered = rendered.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  rendered = rendered.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // Handle underscores for bold/italic as well
  rendered = rendered.replace(/___([^_]+)___/g, "<strong><em>$1</em></strong>");
  rendered = rendered.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  rendered = rendered.replace(/_([^_]+)_/g, "<em>$1</em>");

  return rendered;
}

function resolveLink(currentPath, href) {
  if (/^(https?:)?\/\//.test(href)) {
    return { internal: false, path: href };
  }
  if (!href.endsWith(".md")) {
    return { internal: false, path: href };
  }
  const currentParts = currentPath.split("/").slice(0, -1);
  const rawParts = [...currentParts, ...href.split("/")];
  const normalized = [];
  for (const part of rawParts) {
    if (!part || part === ".") continue;
    if (part === "..") {
      normalized.pop();
      continue;
    }
    normalized.push(part);
  }
  return { internal: true, path: normalized.join("/") };
}

function highlightCode(code, language = "") {
  // Basic syntax highlighting for common languages
  const keywords = /\b(function|const|let|var|if|else|for|while|return|import|export|class|extends|async|await|try|catch|throw|new|this|super|static|public|private|protected|def|lambda|yield|from|as|with|pass|break|continue|in|is|not|and|or|True|False|None|null|undefined|void|int|string|bool|float|double|char)\b/g;
  const strings = /(["'`])(?:(?=(\\?))\2.)*?\1/g;
  const numbers = /\b(\d+\.?\d*)\b/g;
  const comments = /(\/\/.*$|\/\*[\s\S]*?\*\/|#.*$)/gm;
  const functions = /\b([a-zA-Z_]\w*)\s*(?=\()/g;

  let highlighted = escapeHtml(code);

  // Apply highlighting in order (comments first to avoid conflicts)
  highlighted = highlighted.replace(comments, '<span class="comment">$1</span>');
  highlighted = highlighted.replace(strings, '<span class="string">$1</span>');
  highlighted = highlighted.replace(keywords, '<span class="keyword">$1</span>');
  highlighted = highlighted.replace(numbers, '<span class="number">$1</span>');
  highlighted = highlighted.replace(functions, '<span class="function">$1</span>');

  return highlighted;
}

function renderMarkdown(markdown = "", currentPath = "") {
  const lines = markdown.replace(/\r/g, "").split("\n");
  const out = [];
  let inList = false;
  let inCode = false;
  let codeBuffer = [];
  let codeLanguage = "";
  let listTag = "ul";

  const flushList = () => {
    if (inList) {
      out.push(`</${listTag}>`);
      inList = false;
    }
  };

  const flushCode = () => {
    if (inCode) {
      const code = codeBuffer.join("\n");
      const highlighted = highlightCode(code, codeLanguage);
      out.push(`<pre><code>${highlighted}</code></pre>`);
      codeBuffer = [];
      codeLanguage = "";
      inCode = false;
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    const trimmed = line.trim();

    if (trimmed.startsWith("```")) {
      flushList();
      if (inCode) {
        flushCode();
      } else {
        inCode = true;
        codeLanguage = trimmed.slice(3).trim();
      }
      continue;
    }

    if (inCode) {
      codeBuffer.push(rawLine);
      continue;
    }

    if (!trimmed) {
      flushList();
      out.push("");
      continue;
    }

    if (/^#{1,6}\s+/.test(trimmed)) {
      flushList();
      const level = trimmed.match(/^#+/)[0].length;
      const title = trimmed.slice(level).trim();
      const slug = slugify(title);
      out.push(`<h${level} id="${slug}">${inlineMarkdown(title, currentPath)}</h${level}>`);
      continue;
    }

    const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (orderedMatch || trimmed.startsWith("- ")) {
      const targetTag = orderedMatch ? "ol" : "ul";
      const content = orderedMatch ? orderedMatch[2] : trimmed.slice(2);
      if (!inList || listTag !== targetTag) {
        flushList();
        listTag = targetTag;
        out.push(`<${listTag}>`);
        inList = true;
      }
      out.push(`<li>${inlineMarkdown(content, currentPath)}</li>`);
      continue;
    }

    if (trimmed.startsWith("> ")) {
      flushList();
      out.push(`<blockquote>${inlineMarkdown(trimmed.slice(2), currentPath)}</blockquote>`);
      continue;
    }

    flushList();
    out.push(`<p>${inlineMarkdown(trimmed, currentPath)}</p>`);
  }

  flushList();
  flushCode();
  return out.join("\n");
}

function slugify(text = "") {
  return text
    .toLowerCase()
    .replace(/[^\w\- ]+/g, "")
    .trim()
    .replace(/[\s\-]+/g, "-") || "section";
}

function documentRecord(path) {
  return state.documents[path];
}

function nodeRecord(path) {
  return state.nodes.get(path);
}

function flattenNode(node, paths = []) {
  if (node.index) paths.push(node.index);
  for (const doc of node.documents) paths.push(doc);
  for (const child of node.children) flattenNode(child, paths);
  return paths;
}

function matchesQuery(doc) {
  const q = state.query.trim().toLowerCase();
  if (!q) return true;
  return (
    doc.title.toLowerCase().includes(q) ||
    doc.path.toLowerCase().includes(q) ||
    (doc.excerpt || "").toLowerCase().includes(q)
  );
}

function buildLookups(node, parent = null) {
  state.nodes.set(node.path, { ...node, parent });
  for (const child of node.children) {
    buildLookups(child, node.path);
  }
}

function expandForPath(path) {
  const doc = documentRecord(path);
  if (!doc) return;
  let current = doc.parent ?? ".";
  while (current) {
    state.expanded.add(current);
    const record = nodeRecord(current);
    current = record?.parent ?? null;
  }
}

function searchResults() {
  const q = state.query.trim();
  if (!q) return [];
  return Object.values(state.documents)
    .filter(matchesQuery)
    .sort((a, b) => {
      const aTitle = a.title.toLowerCase().includes(q.toLowerCase()) ? 0 : 1;
      const bTitle = b.title.toLowerCase().includes(q.toLowerCase()) ? 0 : 1;
      return aTitle - bTitle || a.title.localeCompare(b.title);
    })
    .slice(0, 12);
}

function renderSearchResults() {
  const results = searchResults();
  searchResultsEl.innerHTML = "";
  if (!results.length) return;
  for (const doc of results) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "search-result";
    item.innerHTML = `
      <div class="search-result-title">${escapeHtml(doc.title)}</div>
      <div class="search-result-meta">${escapeHtml(doc.path)}</div>
    `;
    item.addEventListener("click", () => openDoc(doc.path));
    searchResultsEl.appendChild(item);
  }
}

function renderTreeNode(node) {
  const candidatePaths = flattenNode(node).map((path) => documentRecord(path));
  if (!candidatePaths.some((doc) => matchesQuery(doc))) return null;

  const wrapper = document.createElement("div");
  wrapper.className = "tree-group";
  wrapper.setAttribute("aria-expanded", String(state.expanded.has(node.path)));

  const header = document.createElement("button");
  header.type = "button";
  header.className = "tree-header";
  header.innerHTML = `
    <span class="tree-caret">▶</span>
    <span class="tree-title">${escapeHtml(node.title)}</span>
    <span class="tree-meta">${node.documentCount}</span>
  `;
  header.addEventListener("click", () => {
    if (state.expanded.has(node.path)) {
      state.expanded.delete(node.path);
    } else {
      state.expanded.add(node.path);
    }
    renderTree();
  });
  wrapper.appendChild(header);

  const children = document.createElement("div");
  children.className = "tree-children";

  if (node.index) {
    const indexDoc = documentRecord(node.index);
    const link = document.createElement("a");
    link.href = `#/${node.index}`;
    link.className = `tree-link${state.activePath === node.index ? " is-active" : ""}`;
    link.textContent = translations[state.uiLang]["chapter-homepage"];
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(node.index);
    });
    children.appendChild(link);
  }

  for (const docPath of node.documents) {
    const doc = documentRecord(docPath);
    if (!matchesQuery(doc)) continue;
    const link = document.createElement("a");
    link.href = `#/${doc.path}`;
    link.className = `tree-link${state.activePath === doc.path ? " is-active" : ""}`;
    link.textContent = doc.title;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(doc.path);
    });
    children.appendChild(link);
  }

  for (const child of node.children) {
    const childEl = renderTreeNode(child);
    if (childEl) children.appendChild(childEl);
  }

  wrapper.appendChild(children);
  return wrapper;
}

function renderTree() {
  treeEl.innerHTML = "";
  const rendered = renderTreeNode(state.manifest.root);
  if (rendered) treeEl.appendChild(rendered);
}

function renderBreadcrumbs(doc) {
  const parts = [];
  let current = doc.parent ?? ".";
  while (current) {
    const node = nodeRecord(current);
    if (!node) break;
    if (node.index) {
      parts.unshift({
        title: documentRecord(node.index).title,
        path: node.index,
      });
    }
    current = node.parent;
  }
  breadcrumbsEl.innerHTML = "";

  // Add home icon
  const homeLink = document.createElement("a");
  homeLink.href = "#/";
  homeLink.textContent = "🏠";
  homeLink.title = "Home";
  homeLink.style.fontSize = "1rem";
  homeLink.addEventListener("click", (event) => {
    event.preventDefault();
    openDoc(".");
  });
  breadcrumbsEl.appendChild(homeLink);

  parts.forEach((part, index) => {
    const sep = document.createElement("span");
    sep.textContent = "›";
    breadcrumbsEl.appendChild(sep);

    const link = document.createElement("a");
    link.href = `#/${part.path}`;
    link.textContent = part.title;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(part.path);
    });
    breadcrumbsEl.appendChild(link);
  });

  if (parts.length || true) {
    const sep = document.createElement("span");
    sep.textContent = "›";
    breadcrumbsEl.appendChild(sep);
  }

  const currentLabel = document.createElement("span");
  currentLabel.textContent = doc.title;
  breadcrumbsEl.appendChild(currentLabel);
}

function renderHeroStats(doc) {
  const node = nodeRecord(doc.parent ?? ".");
  const stats = [
    { label: translations[state.uiLang]["word-count"], value: doc.wordCount ?? 0 },
    { label: translations[state.uiLang]["headings"], value: (doc.headings || []).length },
    { label: translations[state.uiLang]["section-depth"], value: doc.depth ?? 0 },
    { label: translations[state.uiLang]["sibling-docs"], value: (node?.documents || []).length },
  ];
  heroStatsEl.innerHTML = "";
  for (const stat of stats) {
    const el = document.createElement("div");
    el.className = "stat-card";
    el.innerHTML = `
      <div class="stat-label">${escapeHtml(String(stat.label))}</div>
      <div class="stat-value">${escapeHtml(String(stat.value))}</div>
    `;
    heroStatsEl.appendChild(el);
  }
}

function renderMeta(doc) {
  metaEl.innerHTML = "";
  const rows = [
    [translations[state.uiLang]["kind"], doc.kind],
    [translations[state.uiLang]["path"], doc.path],
    [translations[state.uiLang]["updated"], doc.updatedAt ? new Date(doc.updatedAt * 1000).toLocaleString() : translations[state.uiLang]["unknown"]],
    [translations[state.uiLang]["word-count"], doc.wordCount ?? 0],
  ];
  for (const [label, value] of rows) {
    const pill = document.createElement("div");
    pill.className = "meta-pill";
    pill.innerHTML = `<strong>${escapeHtml(label)}:</strong> ${escapeHtml(String(value))}`;
    metaEl.appendChild(pill);
  }
}

function parseViewerHash(hash = location.hash) {
  const raw = decodeURIComponent(hash.replace(/^#\//, ""));
  if (!raw) {
    return { path: "", anchor: "" };
  }
  const anchorIndex = raw.indexOf("::");
  if (anchorIndex === -1) {
    return { path: raw, anchor: "" };
  }
  return {
    path: raw.slice(0, anchorIndex),
    anchor: raw.slice(anchorIndex + 2),
  };
}

function scrollToAnchor(anchor, { behavior = "smooth" } = {}) {
  if (!anchor) {
    return;
  }
  const target = document.getElementById(anchor);
  if (target) {
    target.scrollIntoView({ behavior, block: "start" });
  }
}

function renderToc(doc) {
  tocEl.innerHTML = "";
  if (!(doc.headings || []).length) {
    tocEl.innerHTML = `<div class="empty-state">${translations[state.uiLang]["no-headings"]}</div>`;
    return;
  }
  for (const heading of doc.headings) {
    const link = document.createElement("a");
    link.href = `#/${doc.path}::${heading.slug}`;
    link.className = `toc-link level-${heading.level}`;
    link.textContent = heading.title;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(doc.path, { anchor: heading.slug });
    });
    tocEl.appendChild(link);
  }
}

function renderSiblings(doc) {
  siblingLinksEl.innerHTML = "";
  const parentNode = nodeRecord(doc.parent ?? ".");
  if (!parentNode) {
    siblingLinksEl.innerHTML = `<div class="empty-state">${translations[state.uiLang]["no-nearby"]}</div>`;
    return;
  }
  const candidates = [];
  if (parentNode.index && parentNode.index !== doc.path) candidates.push(parentNode.index);
  for (const item of parentNode.documents) if (item !== doc.path) candidates.push(item);
  for (const child of parentNode.children) if (child.index && child.index !== doc.path) candidates.push(child.index);

  if (!candidates.length) {
    siblingLinksEl.innerHTML = `<div class="empty-state">${translations[state.uiLang]["no-nearby"]}</div>`;
    return;
  }

  for (const path of candidates.slice(0, 8)) {
    const related = documentRecord(path);
    const link = document.createElement("a");
    link.href = `#/${related.path}`;
    link.className = "context-link";
    link.textContent = related.title;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(related.path);
    });
    siblingLinksEl.appendChild(link);
  }
}

function relatedCards(doc) {
  const node = nodeRecord(doc.parent ?? ".");
  const cards = [];
  if (node) {
    for (const child of node.children) {
      if (child.index) cards.push(documentRecord(child.index));
    }
    for (const docPath of node.documents) {
      if (docPath !== doc.path) cards.push(documentRecord(docPath));
    }
  }
  return cards.slice(0, 6);
}

function renderRelated(doc) {
  const cards = relatedCards(doc);
  if (!cards.length) {
    relatedSectionEl.innerHTML = `
      <div class="context-label">${translations[state.uiLang]["continue-exploring"]}</div>
      <div class="empty-state" style="padding: 20px; text-align: center;">
        ${translations[state.uiLang]["no-related"]}
      </div>
    `;
    return;
  }
  relatedSectionEl.innerHTML = `
    <div class="context-label">${translations[state.uiLang]["continue-exploring"]}</div>
    <div class="related-grid">
      ${cards.map((item) => `
        <article class="related-card" data-doc-link="${item.path}">
          <div class="related-label">${escapeHtml(item.kind)}</div>
          <div class="related-title">${escapeHtml(item.title)}</div>
          <div class="related-excerpt">${inlineMarkdown(item.excerpt || "No excerpt available.", item.path)}</div>
        </article>
      `).join("")}
    </div>
  `;

  relatedSectionEl.querySelectorAll("[data-doc-link]").forEach((card) => {
    card.addEventListener("click", () => openDoc(card.dataset.docLink));
  });
}

function enhanceRenderedLinks(currentPath) {
  bodyEl.querySelectorAll("[data-doc-link]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      openDoc(link.dataset.docLink, { anchor: link.dataset.docAnchor || "" });
    });
  });
}

function animateDocumentSwap() {
  bodyEl.classList.remove("is-transitioning");
  void bodyEl.offsetWidth;
  bodyEl.classList.add("is-transitioning");
}

function openDoc(path, options = {}) {
  const doc = documentRecord(path);
  if (!doc) return;
  const { anchor = "", updateHistory = true } = options;

  if (state.activePath === path && anchor) {
    scrollToAnchor(anchor);
    if (updateHistory) {
      history.replaceState(null, "", `#/${doc.path}::${anchor}`);
    }
    return;
  }

  state.activePath = path;
  expandForPath(path);
  renderTree();
  renderSearchResults();
  renderBreadcrumbs(doc);
  renderHeroStats(doc);
  renderMeta(doc);
  renderToc(doc);
  renderSiblings(doc);
  renderRelated(doc);

  titleEl.textContent = doc.title;
  subtitleEl.innerHTML = inlineMarkdown(doc.excerpt || doc.path, doc.path);

  // Detect language and apply appropriate styling
  let lang = state.langPreference;
  if (lang === "auto") {
    lang = detectLanguage(doc.markdown);
  }

  bodyEl.setAttribute("lang", lang);

  // Apply language-specific styling
  if (lang === "zh") {
    bodyEl.style.fontFamily = "'Noto Serif SC', 'Crimson Pro', serif";
    bodyEl.style.letterSpacing = "0.05em";
    bodyEl.style.lineHeight = "1.9";
  } else {
    bodyEl.style.fontFamily = "";
    bodyEl.style.letterSpacing = "";
    bodyEl.style.lineHeight = "";
  }

  const renderedBody = doc.html || renderMarkdown(doc.markdown, doc.path);
  bodyEl.innerHTML = `
    <div class="meta-line">${doc.kind.toUpperCase()} • ${escapeHtml(doc.path)}</div>
    ${renderedBody}
  `;
  enhanceRenderedLinks(doc.path);
  animateDocumentSwap();
  if (updateHistory) {
    history.replaceState(null, "", `#/${doc.path}${anchor ? `::${anchor}` : ""}`);
  }
  if (anchor) {
    requestAnimationFrame(() => scrollToAnchor(anchor));
  }

  // Close sidebar on mobile after opening document
  if (window.innerWidth <= 1280) {
    sidebarEl.classList.remove("is-open");
    sidebarBackdropEl.classList.remove("is-visible");
  }
}

function openHome() {
  openDoc(state.manifest.root.index);
}

function renderInitialState() {
  buildLookups(state.manifest.root);
  const { path, anchor } = parseViewerHash();
  const initialPath = path || state.manifest.root.index;
  renderTree();
  renderSearchResults();
  openDoc(state.documents[initialPath] ? initialPath : state.manifest.root.index, {
    anchor,
    updateHistory: false,
  });
}

async function loadManifest() {
  const response = await fetch("data/knowledge-base.json");
  state.manifest = await response.json();
  state.documents = state.manifest.documents;
  renderInitialState();
}

  searchEl.addEventListener("input", () => {
    state.query = searchEl.value;
    renderSearchResults();
    renderTree();
  });

  searchEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      const first = searchResults()[0];
      if (first) openDoc(first.path);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== searchEl) {
      event.preventDefault();
      searchEl.focus();
      searchEl.select();
    }
  });

  window.addEventListener("hashchange", () => {
    const { path, anchor } = parseViewerHash();
    if (state.documents[path]) {
      openDoc(path, { anchor, updateHistory: false });
    }
  });

  navToggleEl.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log("Nav toggle clicked!");

    const isMobile = window.innerWidth <= 1280;
    const appShell = document.querySelector('.app-shell');

    if (isMobile) {
      // Mobile: toggle overlay sidebar
      sidebarEl.classList.toggle("is-open");
      sidebarBackdropEl.classList.toggle("is-visible");
      console.log("Mobile mode - Sidebar classes:", sidebarEl.className);
    } else {
      // Desktop: toggle sidebar collapse
      appShell.classList.toggle("sidebar-collapsed");
      console.log("Desktop mode - App shell classes:", appShell.className);
    }
  });

  sidebarBackdropEl.addEventListener("click", () => {
    console.log("Backdrop clicked!");
    sidebarEl.classList.remove("is-open");
    sidebarBackdropEl.classList.remove("is-visible");
  });

  homeLinkEl.addEventListener("click", openHome);

  loadManifest().catch((error) => {
    titleEl.textContent = "Viewer Error";
    subtitleEl.textContent = "Could not load knowledge-base data";
    bodyEl.innerHTML = `<pre>${escapeHtml(String(error))}</pre>`;
  });
}
