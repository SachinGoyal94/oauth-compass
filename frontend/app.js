/* OAuth Compass SPA — static frontend for Vercel, API on Render. */
(function () {
  "use strict";
  var API = (window.API_BASE || "").replace(/\/$/, "");
  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  var q = new URLSearchParams(window.location.search);

  /* =================== HOME =================== */
  if (el("grid")) {
    var box = el("search-box"), results = el("search-results"), searchTimer = null;

    fetch(API + "/api/guides").then(function (r) { return r.json(); }).then(function (data) {
      var pubs = data.published || [];
      el("lib-count").textContent = pubs.length + " guides · every claim evidence-tagged";
      el("grid").innerHTML = pubs.map(function (g) {
        var chip = g.managed === true
          ? '<span class="badge badge-managed no-dot">Composio-managed</span>'
          : (g.managed === false ? '<span class="badge badge-byo no-dot">Bring your own</span>' : "");
        return '<a class="card guide-card" href="./guide.html?slug=' + encodeURIComponent(g.slug) + '">' +
          '<div class="card-top"><span class="badge tier-' + esc(g.level) + '">' + esc(g.tier) + '</span>' + chip + '</div>' +
          '<h3>' + esc(g.title) + '</h3><p>' + esc(g.summary) + '</p>' +
          '<div class="card-meta"><span>🛠 ' + esc(g.hands_on) + '</span><span>⏳ approval: ' + esc(g.approval_wait) + '</span></div></a>';
      }).join("");
      el("stats").innerHTML =
        '<span class="stat"><span class="dot"></span><b>' + pubs.length + '</b> verified guides</span>' +
        '<span class="stat"><span class="dot"></span><b>—</b> apps profiled</span>' +
        '<span class="stat"><span class="dot"></span><b>~2 min</b> live generation</span>' +
        '<span class="stat"><span class="dot"></span><b>3</b> difficulty tiers covered</span>';
      var names = pubs.map(function (g) { return g.title.split("—")[0].split("(")[0].trim(); })
        .concat(["Linear", "Airtable", "Zoom", "Figma", "Discord", "DocuSign", "Xero", "Spotify",
                 "HubSpot", "Jira", "Dropbox", "Snowflake", "Trello", "Calendly"]);
      var tickerHTML = names.map(function (n) { return "<span><i></i>" + esc(n) + "</span>"; }).join("");
      el("ticker").innerHTML = tickerHTML + tickerHTML;
      fetch(API + "/api/catalog?limit=1").then(function (r) { return r.json(); })
        .then(function (c) {
          if (c.count) {
            el("catalog-toggle").textContent = "Browse " + c.count + " apps in the Composio catalog";
            var stat = el("stats").children[1];
            if (stat) stat.innerHTML = '<span class="dot"></span><b>' + c.count + '</b> apps profiled';
          }
        }).catch(function () {});
    }).catch(function () {
      el("grid").innerHTML = '<p class="muted">Could not reach the API at <code>' + esc(API || "(same origin)") +
        '</code> — set <code>window.API_BASE</code> in <code>config.js</code>.</p>';
    });

    function renderSearch(data) {
      results.innerHTML = ""; results.hidden = false; var added = 0;
      (data.library || []).forEach(function (g) {
        results.insertAdjacentHTML("beforeend",
          '<a href="./guide.html?slug=' + encodeURIComponent(g.slug) + '">' + esc(g.title) +
          '<span class="sr-kind">Guide ready ✓</span><div class="sr-sub">' + esc(g.tier) + " · " +
          esc(g.hands_on) + " · approval: " + esc(g.approval_wait) + '</div></a>');
        added++;
      });
      (data.catalog || []).slice(0, 5).forEach(function (c) {
        results.insertAdjacentHTML("beforeend",
          '<a href="./generate.html?app=' + encodeURIComponent(c.name) + '">' + esc(c.name) +
          '<span class="sr-kind">' + (c.managed ? "Composio-managed" : "BYO · generatable") + '</span>' +
          '<div class="sr-sub">' + (c.oauth ? "OAuth2 supported" : "auth: " + esc((c.auth_schemes || []).join(", "))) + '</div></a>');
        added++;
      });
      if (!added) {
        results.insertAdjacentHTML("beforeend",
          '<div class="sr-item sr-none">Unknown to us — press Enter to have the agent generate a guide.</div>');
      }
    }
    if (box && results) {
      box.addEventListener("input", function () {
        clearTimeout(searchTimer);
        var query = box.value.trim();
        if (!query) { results.hidden = true; return; }
        searchTimer = setTimeout(function () {
          fetch(API + "/api/search?q=" + encodeURIComponent(query))
            .then(function (r) { return r.json(); }).then(renderSearch).catch(function () { results.hidden = true; });
        }, 180);
      });
      box.addEventListener("keydown", function (e) {
        if (e.key === "Enter") window.location.href = "./generate.html?app=" + encodeURIComponent(box.value.trim());
        if (e.key === "Escape") results.hidden = true;
      });
      document.addEventListener("click", function (e) {
        if (!results.contains(e.target) && e.target !== box) results.hidden = true;
      });
    }

    var toggle = el("catalog-toggle"), panel = el("catalog-panel"), status = el("catalog-status");
    if (toggle && panel) {
      toggle.addEventListener("click", function () {
        if (!panel.hidden) { panel.hidden = true; status.hidden = true; return; }
        status.hidden = false; status.textContent = "Loading catalog…";
        fetch(API + "/api/catalog?limit=120").then(function (r) { return r.json(); }).then(function (data) {
          panel.innerHTML = ""; status.hidden = true; panel.hidden = false;
          (data.items || []).forEach(function (c) {
            panel.insertAdjacentHTML("beforeend",
              '<a class="card catalog-card" href="./generate.html?app=' + encodeURIComponent(c.name) + '">' +
              (c.logo ? '<img src="' + esc(c.logo) + '" alt="" loading="lazy">' : "") +
              '<div class="cat-meta"><div class="cat-name">' + esc(c.name) + '</div>' +
              '<div class="cat-sub">' + (c.managed ? "Composio-managed OAuth" : "Bring your own OAuth app") + '</div></div>' +
              '<span class="go">Generate →</span></a>');
          });
          toggle.textContent = "Hide catalog";
        }).catch(function () { status.textContent = "Could not load the catalog."; });
      });
    }
  }

  /* =================== GUIDE =================== */
  if (el("guide-root")) {
    var slug = q.get("slug"), v = q.get("v");
    if (!slug) { el("guide-root").innerHTML = "<p class='muted'>No guide specified.</p>"; }
    else {
      fetch(API + "/api/guides/" + encodeURIComponent(slug) + (v ? "?v=" + encodeURIComponent(v) : ""))
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(renderGuide)
        .catch(function () {
          el("guide-root").innerHTML = '<section class="hero"><span class="kicker">Not in the library yet</span>' +
            '<h1>No guide for <span class="grad">“' + esc(slug) + '”</span>.</h1>' +
            '<p class="hero-sub">It isn\'t hand-verified yet — but the agent can research it live right now.</p>' +
            '<a class="btn btn-primary" href="./generate.html?app=' + encodeURIComponent(slug) + '">Generate it →</a></section>';
        });
    }

    function renderGuide(d) {
      document.title = d.title + " — OAuth Compass";
      var chips = '<span class="badge tier-' + esc(d.difficulty.level) + '">' + esc(d.difficulty.tier) + " · " +
        esc(d.difficulty.level) + '/5</span>';
      if (d.composio_next.managed === true) chips += '<span class="badge badge-managed no-dot">Composio-managed OAuth</span>';
      else if (d.composio_next.managed === false) chips += '<span class="badge badge-byo no-dot">Bring your own OAuth app</span>';
      if (d.shown_version) chips += '<span class="badge badge-version no-dot">' + esc(d.shown_version) + '</span>';
      chips += '<span class="badge no-dot">checked ' + esc(d.provenance.last_checked || "—") + '</span>';

      var versionsBar = "";
      if (d.versions && d.versions.length > 1) {
        versionsBar = '<div class="versions"><span class="muted text-small">Versions:</span>' +
          d.versions.map(function (x) {
            var on = d.shown_version === x.version;
            return '<a class="btn btn-xs' + (on ? " btn-primary" : "") + '" href="./guide.html?slug=' +
              encodeURIComponent(d.slug) + '&v=' + encodeURIComponent(x.version) + '">' + esc(x.version) + '</a>';
          }).join("") +
          (d.shown_version && d.shown_version !== d.active_version
            ? '<button class="btn btn-xs" type="button" id="activate-btn" data-slug="' + esc(d.slug) +
              '" data-version="' + esc(d.shown_version) + '">Make ' + esc(d.shown_version) + ' active</button>'
            : "") + '</div>';
      }

      var html = '<article class="guide"><header class="guide-head"><div class="badges">' + chips + '</div>' +
        '<h1>' + esc(d.title) + '</h1><p class="lede">' + esc(d.summary) + '</p>' +
        '<div class="timebar">' +
        cell("Hands-on setup", d.time.hands_on) + cell("Approval wait", d.time.approval_wait) +
        cell("Difficulty", d.difficulty.tier + " (" + d.difficulty.level + "/5)") + cell("Verdict", d.time.verdict) +
        '</div>' + versionsBar + '</header>';

      if (d.prerequisites.length) {
        html += '<section class="g-section"><h2>Prerequisites</h2><ul class="prereq-list">' +
          d.prerequisites.map(function (p) {
            return '<li>' + (p.blocking ? '<span class="badge badge-req">required</span>' : '<span class="badge no-dot">optional</span>') +
              '<span><strong>' + esc(p.item) + '</strong>' + (p.detail ? " — " + esc(p.detail) : "") + '</span></li>';
          }).join("") + '</ul></section>';
      }

      html += '<section class="g-section"><h2>Step-by-step</h2><ol class="steps">' +
        d.steps.map(function (s) {
          return '<li class="step" data-n="' + esc(s.n) + '"><div class="step-head"><h3>' + esc(s.title) + '</h3>' +
            (s.agent_automatable
              ? '<span class="badge badge-agent no-dot">⚡ agent-automatable</span>'
              : '<span class="badge badge-human no-dot">🧑 human step</span>') +
            (s.duration ? '<span class="muted text-small">~' + esc(s.duration) + '</span>' : "") +
            '</div>' +
            (s.where ? '<div class="step-where">📍 ' + esc(s.where) + '</div>' : "") +
            '<p>' + esc(s.action) + '</p>' +
            (s.nuances ? '<div class="nuance"><strong>Nuance</strong> — ' + esc(s.nuances) + '</div>' : "") +
            '<div class="evidence-line"><span class="ev ev-' + esc(s.evidence) + '">' + esc(s.evidence) + '</span>' +
            (s.source_url ? '<a href="' + esc(s.source_url) + '" target="_blank" rel="noopener" class="src-link">source ↗</a>' : "") +
            '</div></li>';
        }).join("") + '</ol></section>';

      if (d.gotchas.length) {
        html += '<section class="g-section"><h2>Gotchas that bite people</h2><div class="gotchas">' +
          d.gotchas.map(function (got) {
            return '<div class="gotcha"><h3>' + esc(got.title) + ' <span class="ev ev-' + esc(got.evidence) + '">' +
              esc(got.evidence) + '</span></h3><p>' + esc(got.why_it_matters) + '</p>' +
              (got.how_to_handle ? '<p class="fix"><strong>Handle it:</strong> ' + esc(got.how_to_handle) + '</p>' : "") + '</div>';
          }).join("") + '</div></section>';
      }

      if (d.blockers.length) {
        html += '<section class="g-section"><h2>Common blockers &amp; escalation</h2><ul class="blockers">' +
          d.blockers.map(function (b) {
            return '<li><strong>' + esc(b.issue) + '</strong> — ' + esc(b.how_to_resolve) +
              (b.escalation ? '<span class="muted">Escalation: ' + esc(b.escalation) + '</span>' : "") + '</li>';
          }).join("") + '</ul></section>';
      }

      html += '<section class="g-section"><div class="two-col">' +
        '<div class="avh-panel avh-agent"><h2><span class="avh-icon">🤖</span>What an agent can do for you</h2><ul class="agent-can">' +
        d.agent_vs_human.agent_can.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join("") +
        '</ul></div><div class="avh-panel avh-human"><h2><span class="avh-icon">🧑</span>Where you must take over</h2><ul class="human-must">' +
        d.agent_vs_human.human_must.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join("") +
        '</ul></div></div></section>';

      var cn = d.composio_next, nextHtml;
      if (cn.managed === true) {
        nextHtml = '<p>' + esc(cn.managed_note || "Composio provides the OAuth app for this toolkit — you don't need to register one.") + '</p>';
      } else {
        nextHtml = '<p>Register this redirect URI in the provider console, then create the auth config:</p>' +
          '<pre><code>' + esc(cn.redirect_uri_to_register) + '</code></pre>' +
          (cn.auth_config_fields && cn.auth_config_fields.length
            ? '<p>Required credential fields: ' + cn.auth_config_fields.map(function (f) { return '<code>' + esc(f) + '</code>'; }).join(" ") + '</p>'
            : "") +
          (cn.auth_config_snippet ? '<pre><code>' + esc(cn.auth_config_snippet) + '</code></pre>' : "");
      }
      html += '<section class="g-section composio-next"><h2>Connect it via Composio</h2><div class="panel">' + nextHtml +
        (cn.mcp_note ? '<p class="muted">' + esc(cn.mcp_note) + '</p>' : "") + '</div></section>';

      html += '<section class="g-section"><div class="evidence-panel">' +
        '<h2 style="display:flex;align-items:center;gap:11px;font-size:22px;margin:0 0 14px;">Evidence &amp; provenance</h2>' +
        '<ul class="sources">' + d.sources.map(function (s) {
          return '<li><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.title) + ' ↗</a> — ' + esc(s.what_it_supports) + '</li>';
        }).join("") + '</ul>' +
        (d.unverified && d.unverified.length
          ? '<div class="unverified"><strong>Could not verify — treat with care:</strong><ul>' +
            d.unverified.map(function (u) { return '<li>' + esc(u) + '</li>'; }).join("") + '</ul></div>'
          : "") +
        '<p class="provenance"><span class="badge no-dot">' + esc(d.status) + '</span>' +
        '<span>generated by <code>' + esc(d.provenance.generated_by) + '</code></span>' +
        (d.provenance.verified_by
          ? '<span>· verified by <code>' + esc(d.provenance.verified_by) + '</code></span>'
          : '<span>· <strong>not yet human-verified</strong></span>') +
        '<span>· last checked ' + esc(d.provenance.last_checked || "—") + '</span>' +
        (d.provenance.stale_after ? '<span>· re-verify after ' + esc(d.provenance.stale_after) + '</span>' : "") +
        '</p></div></section></article>';

      el("guide-root").innerHTML = html;

      var act = el("activate-btn");
      if (act) {
        act.addEventListener("click", function () {
          act.disabled = true;
          fetch(API + "/api/guides/" + encodeURIComponent(act.getAttribute("data-slug")) + "/activate", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ version: act.getAttribute("data-version") })
          }).then(function (r) { return r.json(); }).then(function (res) {
            if (res.ok) window.location.href = "./guide.html?slug=" + act.getAttribute("data-slug");
            else { act.disabled = false; act.textContent = res.error || "Failed"; }
          }).catch(function () { act.disabled = false; });
        });
      }
    }
    function cell(label, value) {
      return '<div class="timebar-cell"><span class="muted">' + esc(label) + '</span><strong>' + esc(value) + '</strong></div>';
    }
  }

  /* =================== GENERATE =================== */
  var genBtn = el("gen-btn");
  if (genBtn) {
    var genInput = el("gen-input"), genDeep = el("gen-deep"),
        progress = el("gen-progress"), resultWrap = el("gen-result"),
        resultLink = el("gen-result-link"), idle = el("gen-idle");

    if (q.get("app")) genInput.value = q.get("app");

    function addLine(stage, message) {
      if (idle) idle.remove();
      progress.querySelectorAll(".caret").forEach(function (x) { x.classList.remove("caret"); });
      var line = document.createElement("div");
      line.className = "ev-line stage-" + stage + " caret";
      line.innerHTML = '<span class="ev-stage"></span><span></span>';
      line.children[0].textContent = stage;
      line.children[1].textContent = message;
      progress.appendChild(line);
      progress.scrollTop = progress.scrollHeight;
    }

    function startGeneration(input, deep) {
      if (!input.trim()) { genInput.focus(); return; }
      genBtn.disabled = true; genBtn.textContent = "Generating…";
      progress.innerHTML = ""; resultWrap.hidden = true;
      addLine("start", "Submitting “" + input + "” to the agent…");
      fetch(API + "/api/generate", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: input, deep: !!deep })
      }).then(function (resp) {
        if (!resp.ok || !resp.body) throw new Error("HTTP " + resp.status);
        var reader = resp.body.getReader(), decoder = new TextDecoder(), buffer = "";
        function pump() {
          return reader.read().then(function (chunk) {
            if (chunk.done) { finish(); return; }
            buffer += decoder.decode(chunk.value, { stream: true });
            var parts = buffer.split("\n\n"); buffer = parts.pop();
            parts.forEach(function (block) {
              block.split("\n").forEach(function (line) {
                if (line.indexOf("data:") !== 0) return;
                var payload = line.slice(5).trim();
                if (!payload) return;
                try {
                  var evt = JSON.parse(payload);
                  if (evt.stage === "done" && evt.slug) {
                    var base = "./guide.html?slug=" + encodeURIComponent(evt.slug);
                    resultLink.href = base + (evt.version ? "&v=" + encodeURIComponent(evt.version) : "");
                    resultLink.textContent = evt.version ? "View your new draft (" + evt.version + ") →" : "Open the guide →";
                    var old = document.getElementById("library-link");
                    if (old) old.remove();
                    if (evt.library) {
                      var lib = document.createElement("a");
                      lib.id = "library-link";
                      lib.className = "btn";
                      lib.href = base;
                      lib.textContent = "A verified library guide also exists — view it";
                      resultWrap.insertBefore(lib, resultLink);
                    }
                    resultWrap.hidden = false;
                  }
                  addLine(evt.stage, evt.message || "");
                } catch (err) { /* keepalive */ }
              });
            });
            return pump();
          });
        }
        return pump();
      }).catch(function (err) { addLine("error", "Stream failed: " + err.message); });
      function finish() { genBtn.disabled = false; genBtn.textContent = "Generate guide"; }
    }

    genBtn.addEventListener("click", function () { startGeneration(genInput.value, genDeep && genDeep.checked); });
    genInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") startGeneration(genInput.value, genDeep && genDeep.checked);
    });
    if (genInput.value.trim()) startGeneration(genInput.value, false);
  }

  /* ---------- Motion: cursor glow + reveal ---------- */
  document.querySelectorAll(".card").forEach(function (card) {
    card.addEventListener("pointermove", function (e) {
      var r = card.getBoundingClientRect();
      card.style.setProperty("--mx", (e.clientX - r.left) + "px");
      card.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
      });
    }, { threshold: 0.08 });
    revealEls.forEach(function (x) { io.observe(x); });
  } else {
    revealEls.forEach(function (x) { x.classList.add("in"); });
  }
})();
