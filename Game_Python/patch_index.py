"""Patch pygbag build/web/index.html: inject JWT token bridge script."""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'build/web/index.html'

with open(path) as f:
    html = f.read()

token_script = """<script>
(function(){
  var t = localStorage.getItem("SI3LN_JWT_TOKEN");
  if (t) { window.SI3LN_JWT_TOKEN = t; }
  var u = localStorage.getItem("SI3LN_API_URL");
  if (u) { window.SI3LN_API_URL = u; }
})();
</script>"""

html = re.sub(r'(<script[\s>])', token_script + '\n\\1', html, count=1)

with open(path, 'w') as f:
    f.write(html)

print('token injection done ->', path)
