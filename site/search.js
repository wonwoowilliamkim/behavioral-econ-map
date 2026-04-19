// Client-side search for Behavioral Econ Map

const searchInput = document.getElementById("search");

// Results dropdown
const resultsEl = document.createElement("div");
resultsEl.id = "search-results";
document.querySelector("header").appendChild(resultsEl);

searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q || !window._graphNodes) { resultsEl.style.display = "none"; return; }

  const matches = window._graphNodes
    .filter(n => n.label.toLowerCase().includes(q) ||
                 (n.summary || "").toLowerCase().includes(q) ||
                 (n.authors || []).join(" ").toLowerCase().includes(q))
    .slice(0, 8);

  if (!matches.length) { resultsEl.style.display = "none"; return; }

  resultsEl.innerHTML = matches.map(n => `
    <div class="search-result-item" data-id="${n.id}">
      <div class="type-tag">${n.type}</div>
      <div class="result-label">${n.label}</div>
    </div>
  `).join("");

  resultsEl.style.display = "block";

  resultsEl.querySelectorAll(".search-result-item").forEach(item => {
    item.addEventListener("click", () => {
      const node = window._graphNodes.find(n => n.id === item.dataset.id);
      if (!node) return;

      // Focus node in graph
      const connectedIds = new Set();
      window._graphLinks.each(l => {
        if (l.source.id === node.id) connectedIds.add(l.target.id);
        if (l.target.id === node.id) connectedIds.add(l.source.id);
      });
      selectNode(node, window._graphNodes, window._graphLinks);

      // Pan to node
      const t = d3.zoomTransform(d3.select("#graph").node());
      const scale = t.k;
      d3.select("#graph").transition().duration(600).call(
        d3.zoom().transform,
        d3.zoomIdentity
          .translate(window.innerWidth / 2 - node.x * scale, window.innerHeight / 2 - node.y * scale)
          .scale(scale)
      );

      searchInput.value = "";
      resultsEl.style.display = "none";
    });
  });
});

// Close on outside click
document.addEventListener("click", (e) => {
  if (!e.target.closest("#search") && !e.target.closest("#search-results")) {
    resultsEl.style.display = "none";
  }
});
