// D3.js force-directed graph for Behavioral Public Economics Map

const TYPE_CONFIG = {
  topic:      { color: "#4C9BE8", radius: 22, strokeWidth: 2 },
  subtopic:   { color: "#76E4F7", radius: 14, strokeWidth: 1.5 },
  paper:      { color: "#F6AD55", radius: 10, strokeWidth: 1 },
  researcher: { color: "#68D391", radius: 12, strokeWidth: 1.5 },
};

const LINK_CONFIG = {
  has_subtopic:   { color: "#4C9BE8", opacity: 0.5, width: 2 },
  covers_topic:   { color: "#F6AD55", opacity: 0.2, width: 1 },
  researches:     { color: "#68D391", opacity: 0.2, width: 1 },
  authored:       { color: "#68D391", opacity: 0.3, width: 1.5 },
};

let graphData = null;
let simulation = null;
let activeFilter = "all";
let selectedNode = null;

const svg = d3.select("#graph");
const container = document.getElementById("graph-container");

let width = container.clientWidth;
let height = container.clientHeight;

svg.attr("width", width).attr("height", height);

const g = svg.append("g");

// Zoom
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])
  .on("zoom", (e) => g.attr("transform", e.transform));
svg.call(zoom);

// Zoom controls
document.getElementById("zoom-in").addEventListener("click", () =>
  svg.transition().call(zoom.scaleBy, 1.3));
document.getElementById("zoom-out").addEventListener("click", () =>
  svg.transition().call(zoom.scaleBy, 0.77));
document.getElementById("zoom-reset").addEventListener("click", () =>
  svg.transition().call(zoom.transform, d3.zoomIdentity));

// Load graph data
fetch("graph.json")
  .then(r => r.json())
  .then(data => {
    graphData = data;
    render(data);
  })
  .catch(err => {
    console.error("Failed to load graph.json:", err);
    document.getElementById("graph-container").innerHTML =
      '<p style="color:#718096;padding:40px;text-align:center">Run <code>python scripts/build_graph.py</code> to generate graph.json</p>';
  });

function render(data) {
  const nodes = data.nodes.map(d => ({ ...d }));
  const links = data.links.map(d => ({ ...d }));

  // Arrow markers
  svg.append("defs").selectAll("marker")
    .data(["default"])
    .join("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 20)
    .attr("refY", 0)
    .attr("markerWidth", 4)
    .attr("markerHeight", 4)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#444");

  simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links)
      .id(d => d.id)
      .distance(d => {
        if (d.type === "has_subtopic") return 80;
        if (d.type === "authored") return 60;
        return 120;
      }))
    .force("charge", d3.forceManyBody().strength(d => {
      if (d.type === "topic") return -400;
      if (d.type === "subtopic") return -200;
      return -80;
    }))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(d => TYPE_CONFIG[d.type]?.radius * 1.8 || 20));

  // Links
  const link = g.append("g").attr("class", "links")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke", d => LINK_CONFIG[d.type]?.color || "#444")
    .attr("stroke-opacity", d => LINK_CONFIG[d.type]?.opacity || 0.3)
    .attr("stroke-width", d => LINK_CONFIG[d.type]?.width || 1);

  // Nodes
  const node = g.append("g").attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .attr("class", "node")
    .style("cursor", "pointer")
    .call(d3.drag()
      .on("start", dragStart)
      .on("drag", dragged)
      .on("end", dragEnd))
    .on("click", (e, d) => {
      e.stopPropagation();
      selectNode(d, nodes, links);
    });

  node.append("circle")
    .attr("r", d => TYPE_CONFIG[d.type]?.radius || 10)
    .attr("fill", d => TYPE_CONFIG[d.type]?.color || "#888")
    .attr("fill-opacity", 0.85)
    .attr("stroke", "#fff")
    .attr("stroke-width", d => TYPE_CONFIG[d.type]?.strokeWidth || 1)
    .attr("stroke-opacity", 0.3);

  node.append("text")
    .attr("class", "node-label")
    .attr("dy", d => (TYPE_CONFIG[d.type]?.radius || 10) + 12)
    .text(d => {
      const max = d.type === "paper" ? 32 : 24;
      return d.label.length > max ? d.label.slice(0, max) + "…" : d.label;
    })
    .attr("fill-opacity", d => d.type === "paper" ? 0.6 : 0.9);

  // Click on background → deselect
  svg.on("click", () => {
    selectedNode = null;
    document.getElementById("panel").classList.add("hidden");
    node.selectAll("circle").attr("stroke-opacity", 0.3).attr("fill-opacity", 0.85);
    link.attr("stroke-opacity", d => LINK_CONFIG[d.type]?.opacity || 0.3);
  });

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  // Store for search
  window._graphNodes = nodes;
  window._graphLinks = links;
  window._graphNodeSel = node;
  window._graphLinkSel = link;
}

function selectNode(d, nodes, links) {
  selectedNode = d;

  // Highlight
  window._graphNodeSel.selectAll("circle")
    .attr("fill-opacity", n => n.id === d.id ? 1 : 0.3)
    .attr("stroke-opacity", n => n.id === d.id ? 1 : 0.1);

  const connectedIds = new Set();
  window._graphLinks.each(l => {
    if (l.source.id === d.id) connectedIds.add(l.target.id);
    if (l.target.id === d.id) connectedIds.add(l.source.id);
  });
  window._graphNodeSel.selectAll("circle")
    .attr("fill-opacity", n =>
      n.id === d.id ? 1 : connectedIds.has(n.id) ? 0.7 : 0.2);
  window._graphLinkSel
    .attr("stroke-opacity", l =>
      l.source.id === d.id || l.target.id === d.id
        ? (LINK_CONFIG[l.type]?.opacity || 0.3) * 2
        : 0.05);

  // Panel
  showPanel(d, connectedIds);
}

function showPanel(d, connectedIds) {
  const panel = document.getElementById("panel");
  panel.classList.remove("hidden");

  document.getElementById("panel-type").textContent = d.type.toUpperCase();
  document.getElementById("panel-title").textContent = d.label;
  document.getElementById("panel-summary").textContent = d.summary || d.description || "";

  // Meta
  const meta = document.getElementById("panel-meta");
  const parts = [];
  if (d.year)        parts.push(`${d.year}`);
  if (d.journal)     parts.push(d.journal);
  if (d.authors?.length) parts.push(d.authors.join(", "));
  if (d.affiliation) parts.push(d.affiliation);
  meta.innerHTML = parts.join(" · ");
  if (d.url) meta.innerHTML += ` · <a class="panel-link" href="${d.url}" target="_blank">View paper ↗</a>`;
  if (d.website) meta.innerHTML += ` · <a class="panel-link" href="${d.website}" target="_blank">Website ↗</a>`;
  if (d.key_concepts?.length) {
    meta.innerHTML += `<br><span style="color:#a0aec0">Concepts: ${d.key_concepts.join(", ")}</span>`;
  }

  // Connected nodes
  const linksDiv = document.getElementById("panel-links");
  linksDiv.innerHTML = "<div style='font-size:0.75rem;color:#718096;margin-bottom:6px;font-weight:600'>CONNECTED</div>";

  const allNodes = window._graphNodes;
  connectedIds.forEach(id => {
    const n = allNodes.find(x => x.id === id);
    if (!n) return;
    const cfg = TYPE_CONFIG[n.type] || {};
    const el = document.createElement("div");
    el.className = "connected-node";
    el.innerHTML = `<span class="dot" style="background:${cfg.color || '#888'}"></span>
                    <span>${n.label.length > 40 ? n.label.slice(0, 40) + "…" : n.label}</span>`;
    el.addEventListener("click", () => {
      const connIds = new Set();
      window._graphLinks.each(l => {
        if (l.source.id === n.id) connIds.add(l.target.id);
        if (l.target.id === n.id) connIds.add(l.source.id);
      });
      selectNode(n, allNodes, window._graphLinks);
    });
    linksDiv.appendChild(el);
  });
}

// Filter buttons
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeFilter = btn.dataset.type;

    if (!window._graphNodeSel) return;
    window._graphNodeSel.style("display", d =>
      activeFilter === "all" || d.type === activeFilter ? null : "none");
    window._graphLinkSel.style("display", l => {
      if (activeFilter === "all") return null;
      const src = typeof l.source === "object" ? l.source.type : null;
      const tgt = typeof l.target === "object" ? l.target.type : null;
      return src === activeFilter || tgt === activeFilter ? null : "none";
    });
  });
});

// Close panel
document.getElementById("panel-close").addEventListener("click", () => {
  document.getElementById("panel").classList.add("hidden");
  if (window._graphNodeSel) {
    window._graphNodeSel.selectAll("circle").attr("fill-opacity", 0.85).attr("stroke-opacity", 0.3);
    window._graphLinkSel.attr("stroke-opacity", d => LINK_CONFIG[d.type]?.opacity || 0.3);
  }
});

// Resize
window.addEventListener("resize", () => {
  width = container.clientWidth;
  height = container.clientHeight;
  svg.attr("width", width).attr("height", height);
  if (simulation) simulation.force("center", d3.forceCenter(width / 2, height / 2)).alpha(0.1).restart();
});

function dragStart(e, d) {
  if (!e.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}
function dragged(e, d) { d.fx = e.x; d.fy = e.y; }
function dragEnd(e, d) {
  if (!e.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}
