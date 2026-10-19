#!/usr/bin/env python3
"""Draw pictures of the ICC2 result (placement, clock tree, power grid, full layout) from the
GDS and DEF files, so they can be looked at without a layout viewer.

  python3 tools/render_layout.py            # writes docs/img/*.png

Needs matplotlib.  Layer numbers come from config/render.json (site specific, git-ignored)."""
import json, math, pathlib, re, struct, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Rectangle

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config" / "render.json").read_text())
GDS = ROOT / "icc2" / "MAC4.gds"
DEF = ROOT / "icc2" / "MAC4.def"
OUT = ROOT / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)
METALS = {int(k): v for k, v in CFG["metal_layers"].items()}
METAL_ORDER = [METALS[k] for k in sorted(METALS)]
PALETTE = ["#d95f02", "#1b9e77", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#377eb8", "#666666"]
COLOR = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(METAL_ORDER)}

# ------------------------------------------------------------------ minimal GDSII reader
def real8(b):
    s = -1 if b[0] & 0x80 else 1
    e = (b[0] & 0x7F) - 64
    m = int.from_bytes(b[1:8], "big") / float(1 << 56)
    return s * m * 16 ** e

def read_gds(path):
    d = path.read_bytes()
    i = 0
    structs, name, cur, el = {}, None, None, None
    dbu = 1e-3
    while i + 4 <= len(d):
        n, t = struct.unpack(">HB", d[i:i + 3])
        if n < 4:
            break
        body = d[i + 4:i + n]
        if t == 0x03:   # UNITS: user units per dbu, metres per dbu
            dbu = real8(body[8:16]) * 1e6
        elif t == 0x06:
            name = body.rstrip(b"\0").decode()
            structs[name] = {"bnd": [], "path": [], "sref": []}
        elif t in (0x08, 0x09, 0x0A):
            el = {"k": {8: "bnd", 9: "path", 10: "sref"}[t], "layer": None, "w": 0, "xy": [], "sname": None,
                  "refl": False, "angle": 0.0}
        elif t == 0x0D and el: el["layer"] = struct.unpack(">H", body[:2])[0]
        elif t == 0x0F and el: el["w"] = struct.unpack(">i", body)[0]
        elif t == 0x12 and el: el["sname"] = body.rstrip(b"\0").decode()
        elif t == 0x1A and el: el["refl"] = bool(struct.unpack(">H", body)[0] & 0x8000)
        elif t == 0x1C and el: el["angle"] = real8(body)
        elif t == 0x10 and el:
            v = struct.unpack(">%di" % (len(body) // 4), body)
            el["xy"] = list(zip(v[0::2], v[1::2]))
        elif t == 0x11 and el:
            structs[name][el["k"]].append(el)
            el = None
        i += n
    return structs, dbu

structs, DBU = read_gds(GDS)
TOP = "MAC4"

def cell_bbox(nm):
    pts = [p for e in structs[nm]["bnd"] for p in e["xy"]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs) * DBU, min(ys) * DBU, max(xs) * DBU, max(ys) * DBU

BBOX = {nm: cell_bbox(nm) for nm in structs if structs[nm]["bnd"]}

def place_box(cell, x, y, refl=False, angle=0.0):
    x0, y0, x1, y1 = BBOX[cell]
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for px, py in pts:
        if refl:
            py = -py
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        out.append((x + px * c - py * s, y + px * s + py * c))
    xs, ys = [p[0] for p in out], [p[1] for p in out]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

top = structs[TOP]
boxes_all = []
for e in top["sref"]:
    if e["sname"] in BBOX:
        x, y = e["xy"][0][0] * DBU, e["xy"][0][1] * DBU
        boxes_all.append((e["sname"], place_box(e["sname"], x, y, e["refl"], e["angle"])))

# die area from DEF
dtxt = DEF.read_text()
m = re.search(r"DIEAREA \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \) \( (-?\d+) (-?\d+) \)", dtxt)
vals = list(map(int, m.groups()))
XMAX, YMAX = max(vals[0::2]) / 1000, max(vals[1::2]) / 1000

def new_fig(title):
    fig, ax = plt.subplots(figsize=(8.4, 8.4 * (YMAX + 4) / (XMAX + 4)), dpi=150)
    ax.set_xlim(-1.5, XMAX + 1.5); ax.set_ylim(-1.5, YMAX + 1.5)
    ax.set_aspect("equal"); ax.set_xlabel("x [µm]"); ax.set_ylabel("y [µm]")
    ax.set_title(title, fontsize=11, loc="left")
    ax.add_patch(Rectangle((0, 0), XMAX, YMAX, fill=False, ec="#444", lw=0.8, ls="--"))
    return fig, ax

def pt_per_um(ax):
    fig = ax.figure
    return ax.get_position().width * fig.get_figwidth() * 72 / (ax.get_xlim()[1] - ax.get_xlim()[0])

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150, facecolor="white")
    plt.close(fig)
    print("wrote docs/img/" + name)

# ------------------------------------------------------------------ DEF helpers
comps = {}
sec = re.search(r"COMPONENTS \d+ ;(.*?)END COMPONENTS", dtxt, re.S).group(1)
for mm in re.finditer(r"- (\S+) (\S+)(?: \+ SOURCE \S+)? \+ (?:PLACED|FIXED) \( (-?\d+) (-?\d+) \) (\w+)", sec):
    nm, cell, x, y, orient = mm.groups()
    comps[nm] = (cell, int(x) / 1000, int(y) / 1000, orient)

def comp_box(nm):
    cell, x, y, orient = comps[nm]
    x0, y0, x1, y1 = BBOX[cell]
    w, h = x1 - x0, y1 - y0
    if orient in ("E", "W", "FE", "FW"):
        w, h = h, w
    return x, y, w, h

filler_re = re.compile(CFG["filler_regex"]); clock_re = re.compile(CFG["clock_cell_regex"])
logic = [n for n in comps if not filler_re.search(n) and comps[n][0] in BBOX]
is_flop = lambda n: "_reg" in n
lane_of = lambda n: int(re.match(r"lane_(\d)", n).group(1)) if n.startswith("lane_") else -1
LANE_COL = ["#4c78a8", "#f58518", "#54a24b", "#b279a2"]

# ---- 1. placement colored by lane
fig, ax = new_fig("Placement: cells coloured by MAC lane (dark = flip-flops, red = clock-tree buffers)")
for n in logic:
    x, y, w, h = comp_box(n)
    if clock_re.search(n): fc, ec = "#e0302a", "#8b0000"
    else:
        fc = LANE_COL[lane_of(n)] if lane_of(n) >= 0 else "#bbbbbb"; ec = "#333" if is_flop(n) else "none"
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=0.6 if is_flop(n) else 0, alpha=0.95 if is_flop(n) or clock_re.search(n) else 0.55))
for k in range(4): ax.plot([], [], "s", color=LANE_COL[k], label=f"lane {k}")
ax.plot([], [], "s", color="#e0302a", label="clock buffer"); ax.legend(loc="upper center", ncol=5, fontsize=8, bbox_to_anchor=(0.5, -0.09), frameon=False)
save(fig, "placement.png")

# ---- 2. clock tree from the DEF routing
nets = {}
nsec = re.search(r"\nNETS \d+ ;(.*?)END NETS", dtxt, re.S).group(1)
for blk in re.split(r"\n - ", "\n" + nsec)[1:]:
    nm = blk.split()[0]
    nets[nm] = blk
def segments(blk):
    segs, layer = [], None
    for tok in re.finditer(r"(?:ROUTED|NEW) (\w+)([^\n]*)", blk):
        layer, rest = tok.group(1), tok.group(2)
        pts = re.findall(r"\( (-?\d+|\*) (-?\d+|\*) (?:\d+ )?\)", rest)
        cx = cy = None
        pl = []
        for a, b in pts:
            cx = cx if a == "*" else int(a) / 1000
            cy = cy if b == "*" else int(b) / 1000
            pl.append((cx, cy))
        for p, q in zip(pl, pl[1:]):
            segs.append((layer, p, q))
    return segs
clock_nets = [n for n, b in nets.items() if n == "clk" or any(clock_re.search(c) for c in re.findall(r"\( (\S+) \w+ \)", b))]
fig, ax = new_fig("Clock tree: root buffer(s), branches and the flip-flops they drive")
for n in logic:
    x, y, w, h = comp_box(n)
    ax.add_patch(Rectangle((x, y), w, h, fc="#e4e4e4", ec="none"))
lc = LineCollection([[s[1], s[2]] for n in clock_nets for s in segments(nets[n])], colors="#1f5fbf", linewidths=1.0)
ax.add_collection(lc)
fx = [comp_box(n)[0] + comp_box(n)[2] / 2 for n in logic if is_flop(n)]
fy = [comp_box(n)[1] + comp_box(n)[3] / 2 for n in logic if is_flop(n)]
ax.scatter(fx, fy, s=14, c="#111", zorder=3, label=f"flip-flop sinks ({len(fx)})")
bx = [(comp_box(n)[0] + comp_box(n)[2] / 2, comp_box(n)[1] + comp_box(n)[3] / 2) for n in logic if clock_re.search(n)]
ax.scatter([b[0] for b in bx], [b[1] for b in bx], s=90, marker="s", c="#e0302a", ec="#8b0000", zorder=4, label=f"clock buffers ({len(bx)})")
ax.plot([], [], color="#1f5fbf", label="clock wires"); ax.legend(loc="upper center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.09), frameon=False)
save(fig, "clock_tree.png")

# ---- 3. power grid (special nets)
ssec = re.search(r"SPECIALNETS \d+ ;(.*?)END SPECIALNETS", dtxt, re.S).group(1)
fig, ax = new_fig("Power grid: horizontal rails on the lowest metal, vertical straps on the top metal")
for blk in re.split(r"\n - ", "\n" + ssec)[1:]:
    nm = blk.split()[0]
    if nm not in ("VDD", "VSS"):
        continue
    col = "#c0392b" if nm == "VDD" else "#1f5fbf"
    for tok in re.finditer(r"(?:ROUTED|NEW) (\w+) (\d+)[^(]*\( (-?\d+) (-?\d+) \) \( (\*|-?\d+) (\*|-?\d+)", blk):
        layer, w, x1, y1, x2, y2 = tok.groups()
        x1, y1 = int(x1) / 1000, int(y1) / 1000
        x2 = x1 if x2 == "*" else int(x2) / 1000; y2 = y1 if y2 == "*" else int(y2) / 1000
        lw = max(0.6, int(w) / 1000 * pt_per_um(ax))
        ax.plot([x1, x2], [y1, y2], color=col, lw=lw, solid_capstyle="butt", alpha=0.9 if layer == METAL_ORDER[-2] else 0.7)
ax.plot([], [], color="#c0392b", label="VDD"); ax.plot([], [], color="#1f5fbf", label="VSS"); ax.legend(loc="upper center", ncol=2, fontsize=8, bbox_to_anchor=(0.5, -0.09), frameon=False)
save(fig, "power_grid.png")

# ---- 4. full layout from the GDS: cell outlines + signal and power routing
fig, ax = new_fig("Final layout (GDS): cell outlines and routing, one colour per metal layer")
ax.add_collection(PatchCollection([Rectangle((b[0], b[1]), b[2], b[3]) for nm, b in boxes_all],
                                  fc="#f1f1f1", ec="#cfcfcf", lw=0.15))
ppu = pt_per_um(ax)
for layer in sorted(METALS):
    segs, lw_list = [], []
    for e in top["path"]:
        if e["layer"] != layer: continue
        pts = [(x * DBU, y * DBU) for x, y in e["xy"]]
        for p, q in zip(pts, pts[1:]): segs.append([p, q])
    if segs:
        w = [e for e in top["path"] if e["layer"] == layer][0]["w"] * DBU
        ax.add_collection(LineCollection(segs, colors=COLOR[METALS[layer]], linewidths=max(0.35, w * ppu), alpha=0.85))
    ax.plot([], [], color=COLOR[METALS[layer]], lw=2, label=METALS[layer])
ax.legend(loc="upper center", ncol=8, fontsize=8, bbox_to_anchor=(0.5, -0.09), frameon=False)
save(fig, "layout.png")
