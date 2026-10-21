import re, os
d = os.path.dirname(os.path.abspath(__file__))

p = os.path.join(d, "app.py")
s = open(p, encoding="utf-8").read()
s = re.sub(r'@app\.route\("/metrics".*?(?=@app\.route\("/health")', '', s, flags=re.S)
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(d, "index.html")
h = open(p, encoding="utf-8").read()
h = re.sub(r'  #perf \{ margin-top.*?(?=</style>)', '', h, flags=re.S)
h = re.sub(r'<div id="perf">.*?</div></div>\s*(?=<div class="foot">)', '', h, flags=re.S)
h = re.sub(r'fetch\("/metrics"\).*?(?=</script>)', '', h, flags=re.S)
open(p, "w", encoding="utf-8").write(h)
print("reverted")
