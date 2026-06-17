/* PhishGuard web dashboard — client-side inference. No backend, no uploads.
 * Feature extraction is a faithful port of src/phishguard/features.py. */
"use strict";

const $ = (id) => document.getElementById(id);

const SUSPICIOUS_WORDS = ["login", "verify", "secure", "account", "update", "confirm",
  "signin", "sign-in", "banking", "webscr", "password", "billing", "alert", "suspend",
  "unlock", "validate", "wallet"];
const BAD_TLDS = ["tk", "ml", "ga", "cf", "gq", "xyz", "top", "club", "online", "info",
  "click", "work", "support", "zip", "country", "stream"];
const BRANDS = ["paypal", "apple", "microsoft", "amazon", "netflix", "google", "facebook",
  "instagram", "hdfc", "sbi", "icici", "irctc", "whatsapp", "flipkart"];
const IP_RE = /^\d{1,3}(\.\d{1,3}){3}$/;
const FEATURE_NAMES = ["url_length", "host_length", "path_length", "num_dots", "num_hyphens",
  "num_digits_host", "digit_ratio_host", "num_subdomains", "num_query_params", "num_special",
  "has_ip", "has_at", "uses_https", "has_suspicious_word", "suspicious_tld",
  "brand_in_subdomain", "host_entropy", "double_slash_redirect"];

function entropy(s) {
  if (!s) return 0;
  const counts = {};
  for (const ch of s) counts[ch] = (counts[ch] || 0) + 1;
  const n = s.length;
  return -Object.values(counts).reduce((a, c) => a + (c / n) * Math.log2(c / n), 0);
}
function countChar(s, ch) { let n = 0; for (const c of s) if (c === ch) n++; return n; }

// Faithful port of features.extract()
function extract(url) {
  let raw = (url || "").trim();
  if (!raw.includes("://")) raw = "http://" + raw;
  const u = new URL(raw); // throws on invalid → caller handles
  const host = (u.hostname || "").toLowerCase();
  const path = u.pathname || "";
  const query = u.search.startsWith("?") ? u.search.slice(1) : u.search;

  const labels = host ? host.split(".") : [];
  const registered = labels.length >= 2 ? labels.slice(-2).join(".") : host;
  const subdomain = labels.length > 2 ? labels.slice(0, -2).join(".") : "";
  const digitsHost = (host.match(/\d/g) || []).length;
  const tld = labels.length ? labels[labels.length - 1] : "";
  const low = raw.toLowerCase();

  return {
    url_length: raw.length,
    host_length: host.length,
    path_length: path.length,
    num_dots: countChar(host, "."),
    num_hyphens: countChar(raw, "-"),
    num_digits_host: digitsHost,
    digit_ratio_host: host.length ? digitsHost / host.length : 0,
    num_subdomains: Math.max(0, labels.length - 2),
    num_query_params: query ? query.split("&").length : 0,
    num_special: "@%=&?_~".split("").reduce((a, c) => a + countChar(raw, c), 0),
    has_ip: IP_RE.test(host) ? 1 : 0,
    has_at: raw.includes("@") ? 1 : 0,
    uses_https: u.protocol === "https:" ? 1 : 0,
    has_suspicious_word: SUSPICIOUS_WORDS.some((w) => low.includes(w)) ? 1 : 0,
    suspicious_tld: BAD_TLDS.includes(tld) ? 1 : 0,
    brand_in_subdomain: BRANDS.some((b) => subdomain.includes(b) && !registered.includes(b)) ? 1 : 0,
    host_entropy: entropy(host),
    double_slash_redirect: raw.lastIndexOf("//") > 7 ? 1 : 0,
  };
}
function vectorize(url) { const f = extract(url); return FEATURE_NAMES.map((n) => f[n]); }

function sigmoid(z) { return z < -35 ? 0 : z > 35 ? 1 : 1 / (1 + Math.exp(-z)); }

// ---- model ----
let MODEL = null;
async function loadModel() {
  if (MODEL) return MODEL;
  const res = await fetch("model.json", { cache: "no-cache" });
  if (!res.ok) throw new Error("model fetch failed");
  MODEL = await res.json();
  return MODEL;
}
function infer(model, x) {
  const z = x.map((v, j) => (v - model.means[j]) / model.stds[j]);
  const score = model.bias + z.reduce((a, _, j) => a + model.weights[j] * z[j], 0);
  const prob = sigmoid(score);
  const contribs = z.map((zv, j) => ({ feature: FEATURE_NAMES[j], value: model.weights[j] * zv }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .filter((c) => Math.abs(c.value) > 1e-6)
    .slice(0, 6);
  return { prob, contribs };
}

// ---- UI states ----
const states = ["state-empty", "state-loading", "state-result", "state-error"];
function show(which) { states.forEach((s) => ($(s).hidden = s !== which)); }

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function renderResult(url, prob, contribs) {
  const phishing = prob >= 0.5;
  const conf = phishing ? prob : 1 - prob;
  const label = $("verdict-label");
  label.textContent = phishing ? "⚠ Phishing" : "✓ Legitimate";
  label.className = "verdict-label " + (phishing ? "phishing" : "legit");
  $("verdict-conf").textContent = `${(prob * 100).toFixed(1)}% phishing · ${(conf * 100).toFixed(0)}% confidence`;
  const fill = $("gauge-fill");
  fill.style.width = (prob * 100).toFixed(1) + "%";
  fill.style.background = phishing ? "var(--red)" : "var(--green)";
  $("verdict-url").textContent = url;

  const maxAbs = Math.max(...contribs.map((c) => Math.abs(c.value)), 0.001);
  $("explain-list").innerHTML = contribs.map((c) => {
    const up = c.value > 0;
    const w = Math.round((Math.abs(c.value) / maxAbs) * 100);
    return `<li>
      <span class="exp-dir ${up ? "up" : "down"}">${up ? "↑ phishing" : "↓ legit"}</span>
      <span class="exp-feat">${escapeHtml(c.feature)}</span>
      <span class="exp-bar"><span style="width:${w}%;background:${up ? "var(--red)" : "var(--green)"}"></span></span>
    </li>`;
  }).join("");
  show("state-result");
}

async function analyze(url) {
  $("error-msg").hidden = true;
  url = (url || "").trim();
  if (!url) { showError("Please enter a URL."); return; }
  show("state-loading");
  let vec;
  try { vec = vectorize(url); }
  catch (_) { show("state-empty"); showError("That doesn't look like a valid URL."); return; }
  try {
    const model = await loadModel();
    // tiny delay so the skeleton is perceptible on fast machines
    await new Promise((r) => setTimeout(r, 250));
    const { prob, contribs } = infer(model, vec);
    renderResult(url, prob, contribs);
  } catch (e) {
    $("error-state-text").textContent = "Couldn't load the detection model. Check your connection and retry.";
    show("state-error");
  }
}
function showError(msg) { const e = $("error-msg"); e.textContent = msg; e.hidden = false; }

// ---- theme ----
function initTheme() {
  const saved = localStorage.getItem("pg-theme");
  const theme = saved || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  setTheme(theme);
  $("theme-toggle").addEventListener("click", () =>
    setTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark"));
}
function setTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  $("theme-toggle").textContent = t === "dark" ? "🌙" : "☀️";
  localStorage.setItem("pg-theme", t);
}

// ---- footer ----
function renderFooter() {
  const socials = {
    LinkedIn: "https://in.linkedin.com/in/aashana1012",
    GitHub: "https://github.com/aashishbharti04",
    YouTube: "https://www.youtube.com/@CodeWithAsur",
    Instagram: "https://www.instagram.com/asurwave1012",
  };
  const ICON = {
    LinkedIn: '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.13 1.45-2.13 2.94v5.67H9.35V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.38-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14ZM7.12 20.45H3.55V9h3.57v11.45ZM22.22 0H1.77C.8 0 0 .77 0 1.73v20.54C0 23.23.8 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/>',
    GitHub: '<path d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.92c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.34-1.3-1.7-1.3-1.7-1.06-.72.08-.71.08-.71 1.17.08 1.79 1.2 1.79 1.2 1.04 1.79 2.73 1.27 3.4.97.1-.75.4-1.27.73-1.56-2.56-.29-5.26-1.28-5.26-5.7 0-1.26.45-2.29 1.2-3.1-.12-.3-.52-1.46.11-3.05 0 0 .98-.31 3.2 1.18a11.1 11.1 0 0 1 5.83 0c2.22-1.5 3.2-1.18 3.2-1.18.63 1.59.23 2.75.11 3.05.75.81 1.2 1.84 1.2 3.1 0 4.43-2.7 5.4-5.27 5.69.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5Z"/>',
    YouTube: '<path d="M23.5 6.2a3.02 3.02 0 0 0-2.12-2.14C19.5 3.55 12 3.55 12 3.55s-7.5 0-9.38.51A3.02 3.02 0 0 0 .5 6.2 31.6 31.6 0 0 0 0 12a31.6 31.6 0 0 0 .5 5.8 3.02 3.02 0 0 0 2.12 2.14c1.88.51 9.38.51 9.38.51s7.5 0 9.38-.51a3.02 3.02 0 0 0 2.12-2.14A31.6 31.6 0 0 0 24 12a31.6 31.6 0 0 0-.5-5.8ZM9.6 15.6V8.4l6.2 3.6-6.2 3.6Z"/>',
    Instagram: '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16ZM12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.12 1.38C1.35 2.67.94 3.34.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.8.72 1.47 1.38 2.13.66.66 1.33 1.07 2.12 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56a5.9 5.9 0 0 0 2.13-1.38 5.9 5.9 0 0 0 1.38-2.13c.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91a5.9 5.9 0 0 0-1.38-2.12A5.9 5.9 0 0 0 19.86.63c-.76-.3-1.64-.5-2.91-.56C15.67.01 15.26 0 12 0Zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32ZM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm6.41-10.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88Z"/>',
  };
  const links = Object.entries(socials).map(([k, u]) =>
    `<a href="${u}" target="_blank" rel="noopener" aria-label="${k}" title="${k}"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">${ICON[k]}</svg></a>`).join("");
  const year = new Date().getFullYear();
  $("footer").innerHTML = `
    <div class="footer-inner">
      <div>
        <h3>🛡️ PhishGuard</h3>
        <p>An explainable, privacy-first phishing-URL detector. Open source and free for
          educational, learning, and community use.</p>
        <div class="foot-socials">${links}</div>
      </div>
      <div>
        <h3>Project</h3>
        <ul>
          <li><a href="https://github.com/aashishbharti04/phishguard" target="_blank" rel="noopener">Source code</a></li>
          <li><a href="https://github.com/aashishbharti04/phishguard/blob/main/docs/REPORT.md" target="_blank" rel="noopener">Documentation</a></li>
          <li><a href="https://github.com/aashishbharti04/phishguard/issues" target="_blank" rel="noopener">Report an issue</a></li>
        </ul>
      </div>
      <div>
        <h3>Contact</h3>
        <ul>
          <li><a href="mailto:aashish@marketdoctorsonline.com">aashish@marketdoctorsonline.com</a></li>
          <li><a href="https://in.linkedin.com/in/aashana1012" target="_blank" rel="noopener">LinkedIn</a></li>
          <li><a href="https://www.youtube.com/@CodeWithAsur" target="_blank" rel="noopener">YouTube</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">© ${year} PhishGuard. All rights reserved. · Open source — free for educational, learning &amp; community contributions.</div>`;
}

// ---- wiring ----
$("form").addEventListener("submit", (e) => { e.preventDefault(); analyze($("url-input").value); });
document.querySelectorAll(".chip[data-example]").forEach((c) =>
  c.addEventListener("click", () => { $("url-input").value = c.dataset.example; analyze(c.dataset.example); }));

initTheme();
renderFooter();
