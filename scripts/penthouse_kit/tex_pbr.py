import numpy as np
from PIL import Image
import time

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_rgb(arr):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')


def _hex(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _smooth_noise(size, rng, octaves=4, base=4, persistence=0.5):
    """Tileable value-noise via bilinear upsampling of random grids."""
    out = np.zeros((size, size), dtype=np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        g = base * (2 ** o)
        g = max(2, min(g, size))
        grid = rng.random((g, g)).astype(np.float32)
        ys = np.linspace(0, g, size, endpoint=False, dtype=np.float32)
        xs = np.linspace(0, g, size, endpoint=False, dtype=np.float32)
        y0 = np.floor(ys).astype(np.int32)
        x0 = np.floor(xs).astype(np.int32)
        y1 = (y0 + 1) % g
        x1 = (x0 + 1) % g
        fy = (ys - y0)[:, None]
        fx = (xs - x0)[None, :]
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        a = grid[y0][:, x0]
        b = grid[y0][:, x1]
        c = grid[y1][:, x0]
        d = grid[y1][:, x1]
        top = a * (1 - fx) + b * fx
        bot = c * (1 - fx) + d * fx
        n = top * (1 - fy) + bot * fy
        out += n * amp
        total += amp
        amp *= persistence
    out /= total
    return out


def _fbm_1d(size, rng, octaves=5, base=8, persistence=0.55):
    out = np.zeros(size, dtype=np.float32)
    amp = 1.0
    total = 0.0
    for o in range(octaves):
        g = base * (2 ** o)
        g = max(2, min(g, size))
        grid = rng.random(g).astype(np.float32)
        xs = np.linspace(0, g, size, endpoint=False, dtype=np.float32)
        x0 = np.floor(xs).astype(np.int32)
        x1 = (x0 + 1) % g
        fx = xs - x0
        fx = fx * fx * (3 - 2 * fx)
        n = grid[x0] * (1 - fx) + grid[x1] * fx
        out += n * amp
        total += amp
        amp *= persistence
    out /= total
    return out


# ---------------------------------------------------------------------------
# 1. Herringbone oak
# ---------------------------------------------------------------------------

def make_herringbone_oak_tex(size=2048):
    rng = np.random.default_rng(101)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    plank_len = size / 8.0
    plank_wid = size / 16.0

    c = np.cos(np.pi / 4)
    s = np.sin(np.pi / 4)
    xr = (xx - W / 2) * c + (yy - H / 2) * s
    yr = -(xx - W / 2) * s + (yy - H / 2) * c

    cell = plank_len
    cx = np.floor(xr / cell)
    cy = np.floor(yr / cell)
    parity = (cx + cy) % 2

    lx = xr - cx * cell
    ly = yr - cy * cell

    row_idx_h = np.floor(ly / plank_wid)
    col_idx_v = np.floor(lx / plank_wid)

    def hash2(a, b, c_):
        v = np.sin(a * 12.9898 + b * 78.233 + c_ * 37.719) * 43758.5453
        return v - np.floor(v)

    pid_h = hash2(cx, cy, row_idx_h)
    pid_v = hash2(cx, cy, col_idx_v)
    pid = np.where(parity < 0.5, pid_h, pid_v)

    grain_coord = np.where(parity < 0.5, lx, ly)
    cross_coord = np.where(parity < 0.5, ly, lx)

    phase = pid * 100.0
    grain = np.sin(grain_coord * 0.35 + phase) * 0.5 + 0.5
    grain2 = np.sin(grain_coord * 1.1 + phase * 1.7) * 0.5 + 0.5
    grain3 = np.sin(grain_coord * 3.3 + phase * 2.3) * 0.5 + 0.5
    grain_comb = grain * 0.5 + grain2 * 0.3 + grain3 * 0.2

    cross = np.sin(cross_coord * 0.15 + pid * 50) * 0.5 + 0.5

    # Brighter pale-honey oak palette
    base_light = _hex('#EBD6B4')
    base_dark = _hex('#D4B58C')
    t = np.clip(pid * 0.7 + 0.15, 0, 1)
    plank_col = base_light[None, None, :] * (1 - t[..., None]) + base_dark[None, None, :] * t[..., None]

    grain_mod = 0.92 + 0.08 * grain_comb
    grain_mod = grain_mod * (0.97 + 0.03 * cross)
    col = plank_col * grain_mod[..., None]

    edge_h = np.abs(ly - np.round(ly / plank_wid) * plank_wid)
    edge_v = np.abs(lx - np.round(lx / plank_wid) * plank_wid)
    edge = np.where(parity < 0.5, edge_h, edge_v)

    edge_cell_x = np.abs(lx - np.round(lx / cell) * cell)
    edge_cell_y = np.abs(ly - np.round(ly / cell) * cell)
    end_edge = np.where(parity < 0.5, edge_cell_x, edge_cell_y)
    joint = np.minimum(edge, end_edge)

    joint_line = np.clip(1.0 - joint / 2.0, 0, 1)
    joint_dark = 0.78 + 0.22 * joint_line
    col = col * joint_dark[..., None]

    noise = _smooth_noise(size, rng, octaves=3, base=8)
    col = col * (0.98 + 0.04 * noise[..., None])

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# 2. Calacatta marble
# ---------------------------------------------------------------------------

def make_calacatta_marble_tex(size=2048):
    rng = np.random.default_rng(202)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    base = _hex('#F8F5EE')
    col = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]

    n1 = _smooth_noise(size, rng, octaves=5, base=4)
    n2 = _smooth_noise(size, rng, octaves=5, base=4)
    n3 = _smooth_noise(size, rng, octaves=4, base=8)

    warp_x = xx + 80 * (n1 - 0.5)
    warp_y = yy + 80 * (n2 - 0.5)

    vein_field = np.sin((warp_x + warp_y) * 0.012 + n3 * 8.0)
    vein_field2 = np.sin((warp_x - warp_y) * 0.008 + n1 * 6.0)

    vein1 = np.abs(vein_field)
    vein1 = np.clip(1.0 - vein1 * 3.0, 0, 1) ** 2
    vein2 = np.abs(vein_field2)
    vein2 = np.clip(1.0 - vein2 * 4.0, 0, 1) ** 3

    fine = _smooth_noise(size, rng, octaves=6, base=16)
    fine_vein = np.clip(1.0 - np.abs(fine - 0.5) * 8.0, 0, 1) ** 2

    gray_vein = np.clip(vein1 * 0.8 + vein2 * 0.5 + fine_vein * 0.3, 0, 1)

    gold_mask = np.clip(vein1 * 0.6 + fine_vein * 0.4 - 0.15, 0, 1)
    gold_mask = gold_mask * (n3 > 0.5)

    gray_col = _hex('#B6B0A8')
    gold_col = _hex('#C9A663')

    col = col * (1 - gray_vein[..., None] * 0.55) + gray_col[None, None, :] * (gray_vein[..., None] * 0.55)
    col = col * (1 - gold_mask[..., None] * 0.4) + gold_col[None, None, :] * (gold_mask[..., None] * 0.4)

    cloud = _smooth_noise(size, rng, octaves=4, base=3)
    col = col * (0.97 + 0.06 * cloud[..., None])

    col[..., 0] *= 1.01
    col[..., 2] *= 0.99

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# 3. Boucle fabric
# ---------------------------------------------------------------------------

def make_boucle_fabric_tex(size=1024):
    rng = np.random.default_rng(303)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    base = _hex('#F6F0E4')
    col = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]

    n1 = _smooth_noise(size, rng, octaves=4, base=32)
    n2 = _smooth_noise(size, rng, octaves=4, base=64)
    n3 = _smooth_noise(size, rng, octaves=3, base=128)

    loops1 = np.clip((n1 - 0.45) * 6.0, 0, 1)
    loops2 = np.clip((n2 - 0.45) * 8.0, 0, 1)
    loops3 = np.clip((n3 - 0.45) * 10.0, 0, 1)

    loops = loops1 * 0.5 + loops2 * 0.3 + loops3 * 0.2

    fiber = _smooth_noise(size, rng, octaves=5, base=256)
    fiber = (fiber - 0.5) * 0.15

    gy, gx = np.gradient(loops)
    shade = 1.0 + (gx * 0.5 + gy * 0.5) * 2.0
    shade = np.clip(shade, 0.75, 1.25)

    highlight = np.clip(loops * 1.2 - 0.3, 0, 1) * 0.15

    col = col * (shade[..., None] + highlight[..., None] + fiber[..., None])

    warm = _smooth_noise(size, rng, octaves=3, base=8)
    col[..., 0] *= (0.98 + 0.04 * warm)
    col[..., 1] *= (0.98 + 0.03 * warm)
    col[..., 2] *= (0.97 + 0.02 * warm)

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# 4. Travertine
# ---------------------------------------------------------------------------

def make_travertine_tex(size=1024):
    rng = np.random.default_rng(404)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    base = _hex('#E9DEC9')
    col = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]

    band_noise = _fbm_1d(H, rng, octaves=5, base=6, persistence=0.6)
    band_noise_2d = np.tile(band_noise[:, None], (1, W))
    x_var = _smooth_noise(size, rng, octaves=3, base=8)
    band = band_noise_2d * 0.7 + x_var * 0.3

    band_mod = 0.94 + 0.10 * band
    col = col * band_mod[..., None]

    striation = np.sin(yy * 0.8 + band_noise_2d * 20.0) * 0.5 + 0.5
    striation = striation * 0.03
    col = col * (1.0 - striation[..., None])

    pore_noise = _smooth_noise(size, rng, octaves=4, base=64)
    pores = np.clip((pore_noise - 0.62) * 8.0, 0, 1)
    pores = pores * 0.6
    col = col * (1.0 - pores[..., None] * 0.25)

    fine_pore = _smooth_noise(size, rng, octaves=5, base=128)
    fine_pores = np.clip((fine_pore - 0.65) * 10.0, 0, 1) * 0.12
    col = col * (1.0 - fine_pores[..., None])

    overall = _smooth_noise(size, rng, octaves=3, base=4)
    col = col * (0.98 + 0.04 * overall[..., None])

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# 5. Fluted walnut
# ---------------------------------------------------------------------------

def make_fluted_walnut_tex(size=1024):
    rng = np.random.default_rng(505)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    n_flutes = 24
    flute_w = W / n_flutes

    fx = (xx % flute_w) / flute_w
    profile = np.sin(fx * np.pi)
    profile = np.clip(profile, 0, 1)

    light = profile ** 0.7

    crest = _hex('#7A4E32')
    groove = _hex('#3A2214')

    col = groove[None, None, :] * (1 - light[..., None]) + crest[None, None, :] * light[..., None]

    flute_idx = np.floor(xx / flute_w).astype(np.int32)
    grain_1d = _fbm_1d(H, rng, octaves=5, base=16, persistence=0.55)
    phase = (flute_idx % 7) * 0.15
    grain = np.sin(yy * 0.15 + grain_1d[:, None] * 8.0 + phase * 10.0) * 0.5 + 0.5
    grain2 = np.sin(yy * 0.5 + grain_1d[:, None] * 15.0 + phase * 20.0) * 0.5 + 0.5
    grain_comb = grain * 0.6 + grain2 * 0.4

    grain_mod = 0.92 + 0.08 * grain_comb
    col = col * grain_mod[..., None]

    flute_var_1d = (np.sin(np.arange(W, dtype=np.float32) * 12.9898) * 43758.5453) % 1.0
    flute_var_1d = 0.96 + 0.08 * flute_var_1d
    col = col * flute_var_1d[None, :, None]

    edge_dist = np.minimum(xx % flute_w, flute_w - (xx % flute_w))
    groove_line = np.clip(1.0 - edge_dist / 1.5, 0, 1)
    col = col * (1.0 - groove_line[..., None] * 0.4)

    noise = _smooth_noise(size, rng, octaves=3, base=8)
    col = col * (0.98 + 0.04 * noise[..., None])

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# 6. Plush rug
# ---------------------------------------------------------------------------

def make_plush_rug_tex(size=1024):
    rng = np.random.default_rng(606)
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    base = _hex('#F2ECE2')
    col = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]

    n1 = _smooth_noise(size, rng, octaves=5, base=128)
    n2 = _smooth_noise(size, rng, octaves=5, base=256)
    n3 = _smooth_noise(size, rng, octaves=4, base=64)

    fiber = (n1 - 0.5) * 0.12 + (n2 - 0.5) * 0.08 + (n3 - 0.5) * 0.06

    tuft = np.clip((n3 - 0.4) * 4.0, 0, 1)
    tuft_shade = 1.0 + tuft * 0.08

    col = col * (tuft_shade[..., None] + fiber[..., None])

    border_width = size * 0.06
    dist_x = np.minimum(xx, W - 1 - xx)
    dist_y = np.minimum(yy, H - 1 - yy)
    dist_edge = np.minimum(dist_x, dist_y)

    border_inner = border_width
    border_outer = border_width * 2.2

    border_mask = np.clip((dist_edge - border_inner) / 2.0, 0, 1) * np.clip((border_outer - dist_edge) / 2.0, 0, 1)
    border_mask = np.clip(border_mask, 0, 1)

    weave = np.sin(xx * 0.8) * np.sin(yy * 0.8) * 0.5 + 0.5
    weave = weave * 0.3 + 0.7

    border_col = _hex('#D4C4A4')
    border_tex = border_col[None, None, :] * weave[..., None]
    col = col * (1 - border_mask[..., None] * 0.75) + border_tex * (border_mask[..., None] * 0.75)

    edge_line = np.clip(1.0 - np.abs(dist_edge - border_inner) / 1.5, 0, 1)
    edge_line2 = np.clip(1.0 - np.abs(dist_edge - border_outer) / 1.5, 0, 1)
    line_mask = np.clip(edge_line + edge_line2, 0, 1)
    line_col = _hex('#C4B08C')
    col = col * (1 - line_mask[..., None] * 0.5) + line_col[None, None, :] * (line_mask[..., None] * 0.5)

    warm = _smooth_noise(size, rng, octaves=3, base=8)
    col[..., 0] *= (0.98 + 0.04 * warm)
    col[..., 1] *= (0.98 + 0.03 * warm)
    col[..., 2] *= (0.97 + 0.02 * warm)

    return _to_rgb(col)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    funcs = [
        ('herringbone_oak', make_herringbone_oak_tex, 2048),
        ('calacatta_marble', make_calacatta_marble_tex, 2048),
        ('boucle_fabric', make_boucle_fabric_tex, 1024),
        ('travertine', make_travertine_tex, 1024),
        ('fluted_walnut', make_fluted_walnut_tex, 1024),
        ('plush_rug', make_plush_rug_tex, 1024),
    ]
    for name, fn, sz in funcs:
        t0 = time.time()
        img = fn(sz)
        dt = time.time() - t0
        arr = np.asarray(img, dtype=np.float32)
        luma = 0.299 * arr[..., 0].mean() + 0.587 * arr[..., 1].mean() + 0.114 * arr[..., 2].mean()
        print(f'{name}: {img.size} in {dt:.3f}s luma={luma:.1f}')
