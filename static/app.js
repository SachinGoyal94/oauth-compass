/* OAuth Compass client: home search + catalog browse, guide version activation,
   generate page SSE consumption. No frameworks. */
(function () {
  "use strict";

  function el(id) { return document.getElementById(id); }

  /* ---------- Home: search with 3-case resolution ---------- */
  var box = el("search-box");
  var results = el("search-results");
  var searchTimer = null;

  function item(href, main, kind, sub) {
    var a = document.createElement("a");
    a.href = href;
    var mainSpan = document.createElement("span");
    mainSpan.textContent = main;
    a.appendChild(mainSpan);
    if (kind) {
      var k = document.createElement("span");
      k.className = "sr-kind";
      k.textContent = kind;
      a.appendChild(k);
    }
    if (sub) {
      var s = document.createElement("div");
      s.className = "text-small muted";
      s.textContent = sub;
      a.appendChild(s);
    }
    return a;
  }

  function renderSearch(data) {
    results.innerHTML = "";
    results.hidden = false;
    var added = 0;
    (data.library || []).forEach(function (g) {
      results.appendChild(item(g.url, g.title, "Guide ready ✓", g.tier + " · " + g.hands_on + " hands-on · approval: " + g.approval_wait));
      added++;
    });
    (data.catalog || []).slice(0, 5).forEach(function (c) {
      results.appendChild(item(c.generate_url, c.name, c.managed ? "Composio-managed OAuth" : "BYO OAuth · generatable", c.oauth ? "OAuth2 supported" : "auth: " + (c.auth_schemes || []).join(", ")));
      added++;
    });
    if (!added) {
      var none = document.createElement("div");
      none.className = "sr-item sr-none";
      none.textContent = "Unknown to us — press Enter to have the agent generate a guide.";
      results.appendChild(none);
    }
  }

  function hideSearch() { results.hidden = true; }

  if (box && results) {
    box.addEventListener("input", function () {
      clearTimeout(searchTimer);
      var q = box.value.trim();
      if (!q) { hideSearch(); return; }
      searchTimer = setTimeout(function () {
        fetch("/api/search?q=" + encodeURIComponent(q))
          .then(function (r) { return r.json(); })
          .then(renderSearch)
          .catch(hideSearch);
      }, 180);
    });
    box.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        window.location.href = "/generate?app=" + encodeURIComponent(box.value.trim());
      } else if (e.key === "Escape") {
        hideSearch();
      }
    });
    document.addEventListener("click", function (e) {
      if (!results.contains(e.target) && e.target !== box) hideSearch();
    });
  }

  /* ---------- Home: catalog browse ---------- */
  var toggle = el("catalog-toggle");
  var panel = el("catalog-panel");
  var status = el("catalog-status");
  if (toggle && panel) {
    toggle.addEventListener("click", function () {
      if (!panel.hidden) { panel.hidden = true; status.hidden = true; return; }
      status.hidden = false;
      status.textContent = "Loading catalog…";
      fetch("/api/catalog?limit=120")
        .then(function (r) { return r.json(); })
        .then(function (data) {
          panel.innerHTML = "";
          status.hidden = true;
          panel.hidden = false;
          data.items.forEach(function (c) {
            var card = document.createElement("a");
            card.className = "card catalog-card";
            card.href = "/generate?app=" + encodeURIComponent(c.name);
            if (c.logo) {
              var img = document.createElement("img");
              img.src = c.logo; img.alt = ""; img.loading = "lazy";
              card.appendChild(img);
            }
            var meta = document.createElement("div");
            meta.className = "cat-meta";
            var name = document.createElement("div");
            name.className = "cat-name";
            name.textContent = c.name;
            var sub = document.createElement("div");
            sub.className = "cat-sub";
            sub.textContent = c.managed ? "Composio-managed OAuth" : "Bring your own OAuth app";
            meta.appendChild(name); meta.appendChild(sub);
            card.appendChild(meta);
            panel.appendChild(card);
          });
          toggle.textContent = "Hide catalog";
        })
        .catch(function () { status.textContent = "Could not load the catalog."; });
    });
  }

  /* ---------- Guide page: activate a version ---------- */
  var activateBtn = el("activate-btn");
  if (activateBtn) {
    activateBtn.addEventListener("click", function () {
      var slug = activateBtn.getAttribute("data-slug");
      var version = activateBtn.getAttribute("data-version");
      activateBtn.disabled = true;
      fetch("/api/guides/" + encodeURIComponent(slug) + "/activate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: version })
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.ok) { window.location.href = "/guide/" + slug; }
          else { activateBtn.disabled = false; activateBtn.textContent = data.error || "Failed"; }
        })
        .catch(function () { activateBtn.disabled = false; });
    });
  }

  /* ---------- Generate page: SSE stream ---------- */
  var genBtn = el("gen-btn");
  var genInput = el("gen-input");
  var genDeep = el("gen-deep");
  var progress = el("gen-progress");
  var resultWrap = el("gen-result");
  var resultLink = el("gen-result-link");
  var idle = el("gen-idle");

  function addLine(stage, message) {
    if (idle) idle.remove();
    progress.querySelectorAll(".caret").forEach(function (el) { el.classList.remove("caret"); });
    var line = document.createElement("div");
    line.className = "ev-line stage-" + stage + " caret";
    var s = document.createElement("span");
    s.className = "ev-stage";
    s.textContent = stage;
    var m = document.createElement("span");
    m.textContent = message;
    line.appendChild(s); line.appendChild(m);
    progress.appendChild(line);
    progress.scrollTop = progress.scrollHeight;
  }

  function startGeneration(input, deep) {
    if (!input.trim()) { genInput.focus(); return; }
    genBtn.disabled = true;
    genBtn.textContent = "Generating…";
    progress.innerHTML = "";
    resultWrap.hidden = true;
    addLine("start", "Submitting “" + input + "” to the agent…");

    fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: input, deep: !!deep })
    }).then(function (resp) {
      if (!resp.ok || !resp.body) { throw new Error("HTTP " + resp.status); }
      var reader = resp.body.getReader();
      var decoder = new TextDecoder();
      var buffer = "";
      function pump() {
        return reader.read().then(function (chunk) {
          if (chunk.done) { finish(); return; }
          buffer += decoder.decode(chunk.value, { stream: true });
          var parts = buffer.split("\n\n");
          buffer = parts.pop();
          parts.forEach(function (block) {
            block.split("\n").forEach(function (line) {
              if (line.indexOf("data:") !== 0) return;
              var payload = line.slice(5).trim();
              if (!payload) return;
              try {
                var evt = JSON.parse(payload);
                if (evt.stage === "done" && evt.slug) {
                  resultLink.href = "/guide/" + encodeURIComponent(evt.slug) + (evt.version ? "?v=" + encodeURIComponent(evt.version) : "");
                  resultLink.textContent = evt.version ? "View your new draft (" + evt.version + ") →" : "Open the guide →";
                  var old = document.getElementById("library-link");
                  if (old) old.remove();
                  if (evt.library) {
                    var lib = document.createElement("a");
                    lib.id = "library-link";
                    lib.className = "btn";
                    lib.href = "/guide/" + encodeURIComponent(evt.slug);
                    lib.textContent = "A verified library guide also exists — view it";
                    resultWrap.insertBefore(lib, resultLink);
                  }
                  resultWrap.hidden = false;
                }
                addLine(evt.stage, evt.message || "");
              } catch (err) { /* ignore malformed keepalives */ }
            });
          });
          return pump();
        });
      }
      return pump();
    }).catch(function (err) {
      addLine("error", "Stream failed: " + err.message);
    });

    function finish() {
      genBtn.disabled = false;
      genBtn.textContent = "Generate guide";
    }
  }

  if (genBtn) {
    genBtn.addEventListener("click", function () { startGeneration(genInput.value, genDeep && genDeep.checked); });
    genInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") startGeneration(genInput.value, genDeep && genDeep.checked);
    });
    if (genInput.value.trim()) startGeneration(genInput.value, false);
  }

  /* ---------- Motion: cursor glow on cards ---------- */
  document.querySelectorAll(".card").forEach(function (card) {
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", (e.clientX - r.left) + "px");
      card.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  /* ---------- Motion: reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
      });
    }, { threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }
})();
