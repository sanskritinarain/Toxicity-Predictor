import os
d = os.path.dirname(os.path.abspath(__file__))

# 1) app.py: add /metrics route
p = os.path.join(d, "app.py")
s = open(p, encoding="utf-8").read()
marker = '@app.route("/health", methods=["GET"])'
route = '''@app.route("/metrics", methods=["GET"])
def metrics():
    import csv
    from flask import jsonify
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment6_artifacts", "test_metrics.csv")
    with open(f, newline="", encoding="utf-8-sig") as fh:
        return jsonify(list(csv.DictReader(fh)))


'''
if '"/metrics"' not in s:
    if "import os" not in s:
        s = "import os\n" + s
    s = s.replace(marker, route + marker, 1)
    open(p, "w", encoding="utf-8").write(s)

# 2) index.html: add performance panel
p = os.path.join(d, "index.html")
h = open(p, encoding="utf-8").read()
if 'id="perf"' not in h:
    css = '''  #perf { margin-top: 28px; }
  #perf h3 { margin: 0 0 10px; font-size: 16px; }
  #perf table { width: 100%; border-collapse: collapse; font-size: 13px; }
  #perf th, #perf td { padding: 8px 10px; text-align: right; border-bottom: 1px solid #e5e7eb; }
  #perf th:first-child, #perf td:first-child { text-align: left; }
  #perf th { color: #6b7280; font-weight: 600; background: #f9fafb; }
  #perf .note { margin-top: 8px; font-size: 11px; color: #9ca3af; }
  #perf .wrap { overflow-x: auto; }
</style>'''
    h = h.replace("</style>", css, 1)
    html = '''<div id="perf"><h3>Model performance (held-out test set)</h3><div class="wrap" id="perfTable">Loading...</div>
  <div class="note">Accuracy can look high when toxic molecules are rare. ROC-AUC, PR-AUC and F1 are more informative here.</div></div>
  <div class="foot">'''
    h = h.replace('<div class="foot">', html, 1)
    js = '''fetch("/metrics").then(r => r.json()).then(rows => {
  if (!rows.length) { $("perfTable").textContent = "No metrics found."; return; }
  const cols = Object.keys(rows[0]);
  const fmt = v => (v !== "" && !isNaN(v)) ? Number(v).toFixed(3) : esc(v);
  $("perfTable").innerHTML = "<table><tr>" + cols.map(c => "<th>" + esc(c) + "</th>").join("") + "</tr>" +
    rows.map(r => "<tr>" + cols.map(c => "<td>" + fmt(r[c]) + "</td>").join("") + "</tr>").join("") + "</table>";
}).catch(e => { $("perfTable").textContent = "Could not load metrics: " + e; });
</script>'''
    h = h.replace("</script>", js, 1) if False else h[::-1].replace(">tpircs/<", ">tpircs/<"[::-1] if False else js[::-1], 1)[::-1]
    open(p, "w", encoding="utf-8").write(h)
print("patched")
