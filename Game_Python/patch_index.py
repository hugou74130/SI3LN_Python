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

# ── Style overrides ───────────────────────────────────────────────────────────
# The stock pygbag template ships an ugly light-blue ("powderblue") body and a
# green/blue "Loading, please wait" box, and stretches the fixed 1280x720
# framebuffer to fill the iframe (distorting the game). Override all three so the
# loading gap reads as a clean dark screen and the game keeps its 16:9 ratio.
# Rules use !important so they win over the runtime `body.style.background`
# that pygbag sets inline once the WASM module boots.
style_overrides = """<style id="si3ln-overrides">
  html, body { background: #05010f !important; margin: 0; padding: 0; overflow: hidden; }
  /* hide pygbag's default green/blue "Loading, please wait" box */
  #infobox { display: none !important; }
  /* theme the small downloader text / progress bar in case they flash */
  #status { color: #8ea0c8 !important; font-family: 'Courier New', monospace !important; }
  #progress { accent-color: #3a47d5; }
  /* Preserve the game's 16:9 ratio by sizing the CANVAS ELEMENT itself to the
     largest 16:9 box that fits the viewport, centred, with the dark body
     showing through as letterbox bars. We must NOT use object-fit here: that
     would shrink only the painted bitmap while the element box stays full-size,
     so emscripten's pointer mapping (clientX across the full element -> 1280px
     framebuffer) would misalign every mouse click. Sizing the element keeps
     getBoundingClientRect() equal to the visible game, so input stays accurate.
     16/9 = 1.7778 -> 177.78vh ;  9/16 = 0.5625 -> 56.25vw */
  canvas.emscripten, #canvas {
    position: absolute !important;
    top: 50% !important; left: 50% !important;
    right: auto !important; bottom: auto !important;
    transform: translate(-50%, -50%) !important;
    width: min(100vw, 177.78vh) !important;
    height: min(100vh, 56.25vw) !important;
    margin: 0 !important;
    background: #05010f !important;
  }
</style>"""

if '</head>' in html:
    html = html.replace('</head>', style_overrides + '\n</head>', 1)
else:
    # No </head> (pygbag sometimes omits it) — prepend into <body>.
    html = re.sub(r'(<body[\s>])', style_overrides + '\n\\1', html, count=1)

with open(path, 'w') as f:
    f.write(html)

print('token + style injection done ->', path)
