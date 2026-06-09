"""kebab_tqdm -- a tqdm progress bar that shows a kebab-shop scene.

The bearded chef (an ASCII portrait converted from a photo) stands on the right
and shaves a turning doner spit on the left; the shaved meat piles up in the
foil tray as the progress climbs.

    from kebab_tqdm import tqdm
    for x in tqdm(range(100)):
        ...

``kebab_tqdm`` is kept as an alias of ``tqdm`` for backwards compatibility.
"""
import os
from importlib import resources

from tqdm import tqdm as _tqdm

__version__ = "0.1.0"
__all__ = ["tqdm", "kebab_tqdm"]


def _enable_ansi():
    """Turn on ANSI escape handling so the in-place redraw works on Windows."""
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT |
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


_enable_ansi()

# Frames that make the spit look like it is turning.
_SPIN = ["|", "/", "-", "\\"]
_MEAT = ["#", "%", "8", "%"]
# Shading bands wrapped round the cone. Drawn as diagonals that shift every
# frame so the meat looks like it is rotating on the spit.
_MEAT_PALETTE = "@@%%##*+*##%%"

# The chef: an ASCII portrait of the bearded man, shipped as package data.
try:
    _raw = resources.files(__name__).joinpath("chef_scene.txt").read_text(
        encoding="utf-8"
    )
    CHEF = [ln for ln in _raw.split("\n") if ln.strip()]
    # Strip the common left padding (the cleared columns) so the chef isn't
    # shoved to the far right, then pad all rows to the same width.
    _indent = min(len(ln) - len(ln.lstrip(" ")) for ln in CHEF)
    CHEF = [ln[_indent:] for ln in CHEF]
    _CHEF_W = max(len(ln) for ln in CHEF)
    CHEF = [ln.ljust(_CHEF_W) for ln in CHEF]
    _CHEF_H = len(CHEF)
except (OSError, FileNotFoundError):
    CHEF = ["(chef portrait missing: chef_scene.txt)"]
    _CHEF_W = len(CHEF[0])
    _CHEF_H = 1


def _center(s, width):
    pad = width - len(s)
    left = pad // 2
    return " " * left + s + " " * (pad - left)


def _cone_shape(n, top, bottom):
    """Odd meat widths tapering from `top` to `bottom` over `n` rows."""
    shape = []
    for i in range(n):
        w = round(top + (bottom - top) * i / (n - 1))
        if w % 2 == 0:
            w += 1
        shape.append(max(3, w))
    return shape


def _build_kebab(spin, meat, frac, frame):
    """A big turning doner cone with shaved meat piling up in a foil tray."""
    max_pile = 9
    # finial + cone + bare spike + pile + 2 tray rows == chef height, so the
    # grill stands as tall as the chef.
    n_cone = max(8, _CHEF_H - max_pile - 4)
    shape = _cone_shape(n_cone, 19, 5)    # tall cone, wide at the top
    field = max(shape) + 2
    center = field // 2
    pal = _MEAT_PALETTE
    npal = len(pal)

    def cone_row(w, r):
        """One row of meat: diagonal shading bands that shift with `frame`."""
        row = [" "] * field
        left = center - (w + 2) // 2
        row[left] = "["
        row[left + w + 1] = "]"
        for i in range(w):
            c = left + 1 + i
            row[c] = pal[(c - r + frame) % npal]   # diagonals scrolling = spin
        return "".join(row)

    rows = [_center(" %s " % spin, field)]               # finial on the spike
    for r, w in enumerate(shape):
        rows.append(cone_row(w, r))                       # full, turning meat
    bare = [" "] * field
    bare[center] = spin
    rows.append("".join(bare))                            # bare spike below cone

    # Growing pile of shaved meat collecting in the foil tray.
    pile_h = int(round(frac * max_pile))
    for k in range(max_pile - 1, -1, -1):
        if k < pile_h:
            w = min((pile_h - k) * 2 - 1, field - 2)
            rows.append(_center(meat * w, field))
        else:
            rows.append(" " * field)
    rows.append(_center("\\" + "_" * (field - 2) + "/", field))   # foil tray
    rows.append(_center("'" + "=" * (field - 2) + "'", field))    # tray rim
    return rows, field, len(shape)


def _kebab_scene(frac, frame):
    """Compose the scene: turning kebab on the left, chef portrait on the right,
    and a diagonal knife reaching from the chef into the cone."""
    spin = _SPIN[frame % len(_SPIN)]
    meat = _MEAT[frame % len(_MEAT)]

    kebab, field, n_cone = _build_kebab(spin, meat, frac, frame)
    chef = CHEF
    gap = 12                                   # room for a long knife to reach
    cbase = field + gap                       # left column of the chef block

    # Bottom-align both blocks (they share the floor) on a single grid.
    H = max(len(kebab), len(chef))
    W = field + gap + _CHEF_W
    grid = [[" "] * W for _ in range(H)]

    def place(block, r0, c0):
        for i, line in enumerate(block):
            for j, ch in enumerate(line):
                if ch != " ":
                    grid[r0 + i][c0 + j] = ch

    koff = H - len(kebab)
    place(kebab, koff, 0)
    place(chef, H - len(chef), cbase)

    # A long *diagonal* doner knife: a wide blade slanting from its tip up in
    # the meat (upper-left) down to the fist by the chef (lower-right). It
    # shaves a few rows up and down, slowly.
    blade_len = gap + 7
    blade_w = 3                                 # blade thickness
    tip_col = field - 5                         # tip bites into the meat
    amp = 3
    slow = 4                                    # advance the stroke every 4 frames
    phase = (frame // slow) % (2 * amp)
    t = phase if phase <= amp else 2 * amp - phase   # 0..amp..0
    tip_row = koff + n_cone // 2 - blade_len // 2 + t

    def put(r, c, ch, hand=False):
        if 0 <= r < H and 0 <= c < W and (hand or grid[r][c] == " " or c < field):
            grid[r][c] = ch

    for k in range(blade_len):                  # the slanted, thick blade
        for d in range(blade_w):
            edge = d == 0 or d == blade_w - 1
            put(tip_row + k, tip_col + k + d, "\\" if edge else "#")
    put(tip_row, tip_col, "v")                  # pointed tip in the meat

    # A fist gripping the lower-right end of the blade.
    hr, hc = tip_row + blade_len, tip_col + blade_len
    fist = ["   __", "  (##)", " (####)", "(######)", " `----'"]
    for i, frow in enumerate(fist):
        for j, ch in enumerate(frow):
            if ch != " ":
                put(hr - 1 + i, hc - 2 + j, ch, hand=True)

    return ["".join(row).rstrip() for row in grid]


class tqdm(_tqdm):
    """Drop-in ``tqdm`` replacement that renders the kebab scene each refresh."""

    def __init__(self, *args, **kwargs):
        self._frame = 0
        self._prev_lines = 0
        super().__init__(*args, **kwargs)

    def display(self, msg=None, pos=None):
        if self.disable:
            return False

        total = self.total
        frac = (self.n / total) if total else 0.0
        frac = min(max(frac, 0.0), 1.0)

        scene = _kebab_scene(frac, self._frame)
        self._frame += 1

        if total:
            status = f"  shaving kebab... {frac * 100:5.1f}%  ({self.n}/{total})"
        else:
            status = f"  shaving kebab... {self.n} it"
        if self.desc:
            status = f"  {self.desc}{status}"
        scene = scene + [status]

        out = []
        if self._prev_lines:
            out.append(f"\x1b[{self._prev_lines}A")  # cursor up to redraw
        for line in scene:
            out.append("\r\x1b[K" + line + "\n")     # clear line, then draw

        self.fp.write("".join(out))
        self.fp.flush()
        self._prev_lines = len(scene)
        return True


# Backwards-compatible alias.
kebab_tqdm = tqdm
