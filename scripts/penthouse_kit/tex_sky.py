"""Sky panorama textures for the penthouse kit.

Generates a rich California coastal cobalt-cerulean sky with true round
billowing cumulus clouds (never horizontal streaks) plus a calm slate
overcast variant for rainy moods.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _gradient_stops(stops, ys: np.ndarray) -> np.ndarray:
    """stops: list of (pos, rgb). ys: (H,) normalized. returns (H,3)."""
    pos = np.array([s[0] for s in stops], dtype=np.float64)
    cols = np.stack([s[1] for s in stops], axis=0)  # (K,3)
    out = np.empty((ys.shape[0], 3), dtype=np.float64)
    for c in range(3):
        out[:, c] = np.interp(ys, pos, cols[:, c])
    return out


# ---------------------------------------------------------------------------
# sunny sky
# ---------------------------------------------------------------------------

def make_sunny_sky_panorama(w: int = 4096, h: int = 1024) -> Image.Image:
    rng = np.random.default_rng(77)

    # ---- sky vertical gradient -------------------------------------------
    sky_stops = [
        (0.00, _hex_to_rgb("#154690")),  # deep pure cobalt zenith
        (0.20, _hex_to_rgb("#1E5AA0")),
        (0.36, _hex_to_rgb("#2C6DB8")),  # Malibu cerulean
        (0.50, _hex_to_rgb("#5A9CE0")),  # sunlit horizon blue
        (0.58, _hex_to_rgb("#EBF2F7")),  # warm alabaster haze
    ]
    ocean_stops = [
        (0.58, _hex_to_rgb("#245A88")),  # deep Pacific sapphire
        (0.80, _hex_to_rgb("#2E6690")),
        (1.00, _hex_to_rgb("#4478A2")),
    ]

    ys = np.linspace(0.0, 1.0, h, dtype=np.float64)
    sky_col = _gradient_stops(sky_stops, ys)      # (H,3)
    ocean_col = _gradient_stops(ocean_stops, ys)  # (H,3)

    horizon = 0.58
    blend = _smoothstep(horizon - 0.004, horizon + 0.004, ys)[:, None]
    base = sky_col * (1.0 - blend) + ocean_col * blend  # (H,3)

    img = np.repeat(base[:, None, :], w, axis=1)  # (H,W,3)

    # ---- ocean wave shimmer ------------------------------------------------
    xs = np.linspace(0.0, 1.0, w, dtype=np.float64)
    sun_u, sun_v = 0.54, 0.23
    wave_u = xs[None, :] * 110.0 + ys[:, None] * 14.0
    wave_v = ys[:, None] * 165.0
    sea_mask = np.clip((ys - 0.585) / 0.04, 0.0, 1.0)[:, None]
    shimmer = (np.sin(wave_u) * np.cos(wave_v) + np.sin(xs[None, :] * 230.0 - wave_v * 0.7) * 0.6) * 4.5
    sun_lane = np.exp(-(((xs[None, :] - sun_u) / 0.14) ** 2)) * np.exp(-(((ys[:, None] - 0.58) / 0.18) ** 2))
    img[:, :, 0] += sea_mask * (shimmer * 0.7 + sun_lane * 36.0)
    img[:, :, 1] += sea_mask * (shimmer * 0.9 + sun_lane * 38.0)
    img[:, :, 2] += sea_mask * (shimmer * 1.1 + sun_lane * 34.0)

    # ---- warm subtle sun glow --------------------------------------------
    du = (xs[None, :] - sun_u)
    dv = (ys[:, None] - sun_v)
    dist2 = du * du + dv * dv
    glow = np.exp(-dist2 / (2.0 * 0.11 * 0.11))
    glow_col = _hex_to_rgb("#FFF4D8")
    img += glow[:, :, None] * (glow_col[None, None, :] - img) * 0.52

    # ---- multi-scale organic atmospheric fBm noise for wispy cumulus rims ----
    def _upsample_noise(gh: int, gw: int) -> np.ndarray:
        g = rng.random((gh, gw))
        pil_n = Image.fromarray((g * 255.0).astype(np.uint8), mode="L").resize((w, h), resample=Image.BILINEAR)
        return np.asarray(pil_n, dtype=np.float64) / 255.0

    fbm = 0.55 * _upsample_noise(28, 112) + 0.30 * _upsample_noise(64, 256) + 0.15 * _upsample_noise(140, 560)

    # ---- cumulus clouds (evenly jittered across whole sky arc) ------------
    cloud_density = np.zeros((h, w), dtype=np.float64)
    cloud_shade = np.zeros((h, w), dtype=np.float64)

    n_clouds = 18
    cu_slots = np.linspace(0.06, 0.94, n_clouds) + rng.uniform(-0.022, 0.022, n_clouds)
    for cu in cu_slots:
        cv = rng.uniform(0.18, 0.44)
        cx = cu * w
        cy = cv * h

        n_puffs = int(rng.integers(12, 18))
        spread_x = rng.uniform(0.036, 0.068) * w
        spread_y = rng.uniform(0.034, 0.056) * h

        for _p in range(n_puffs):
            ang = rng.uniform(0.0, 2.0 * np.pi)
            rad = np.sqrt(rng.uniform(0.0, 1.0))
            px = cx + np.cos(ang) * rad * spread_x
            py = cy + np.sin(ang) * rad * spread_y
            if py > cy + spread_y * 0.25:
                py = cy + spread_y * 0.25 + (py - (cy + spread_y * 0.25)) * 0.28

            ry = rng.uniform(30.0, 74.0)
            rx = ry * rng.uniform(1.05, 1.25)

            x0 = int(np.floor(px - rx * 1.9))
            x1 = int(np.ceil(px + rx * 1.9))
            y0 = int(np.floor(py - ry * 1.9))
            y1 = int(np.ceil(py + ry * 1.9))
            if x1 <= 0 or y1 <= 0 or x0 >= w or y0 >= h:
                continue
            x0c, x1c = max(x0, 0), min(x1, w)
            y0c, y1c = max(y0, 0), min(y1, h)
            if x1c <= x0c or y1c <= y0c:
                continue

            gx = np.arange(x0c, x1c, dtype=np.float64) + 0.5
            gy = np.arange(y0c, y1c, dtype=np.float64) + 0.5
            dx = (gx[None, :] - px) / rx
            dy = (gy[:, None] - py) / ry
            r2 = dx * dx + dy * dy

            erode = (fbm[y0c:y1c, x0c:x1c] - 0.5) * 0.68
            puff = np.clip(1.0 - np.sqrt(r2 + 1e-6) + erode, 0.0, 1.0)
            puff = puff * puff * (3.0 - 2.0 * puff)

            sub_d = cloud_density[y0c:y1c, x0c:x1c]
            np.maximum(sub_d, puff, out=sub_d)

            shade_row = np.clip((gy - (cy - spread_y)) / (2.1 * spread_y), 0.0, 1.0)
            shade2d = np.broadcast_to(shade_row[:, None], puff.shape)

            sub_s = cloud_shade[y0c:y1c, x0c:x1c]
            mask = puff > sub_s
            sub_s[mask] = shade2d[mask]

    # ---- composite clouds over sky ---------------------------------------
    cov = np.clip(cloud_density * 1.18, 0.0, 1.0)
    cov = cov * cov * (3.0 - 2.0 * cov)

    top_col = _hex_to_rgb("#FFFCF8")
    under_col = _hex_to_rgb("#BCCFE4")
    shade_t = np.clip(cloud_shade, 0.0, 1.0)[:, :, None]
    cloud_col = top_col[None, None, :] * (1.0 - shade_t) + under_col[None, None, :] * shade_t

    img = img * (1.0 - cov[:, :, None]) + cloud_col * cov[:, :, None]

    img = np.clip(img, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


# ---------------------------------------------------------------------------
# rainy sky
# ---------------------------------------------------------------------------

def make_rainy_sky_panorama(w: int = 2048, h: int = 512) -> Image.Image:
    stops = [
        (0.00, _hex_to_rgb("#2B3B4D")),
        (0.35, _hex_to_rgb("#3A4C60")),
        (0.65, _hex_to_rgb("#4A5F76")),
        (1.00, _hex_to_rgb("#556B82")),
    ]
    ys = np.linspace(0.0, 1.0, h, dtype=np.float64)
    col = _gradient_stops(stops, ys)  # (H,3)

    rng = np.random.default_rng(11)
    xs = np.linspace(0.0, 1.0, w, dtype=np.float64)
    mottle = np.zeros((h, w), dtype=np.float64)
    for _ in range(14):
        cu = rng.uniform(0.0, 1.0)
        cv = rng.uniform(0.0, 1.0)
        sx = rng.uniform(0.08, 0.22)
        sy = rng.uniform(0.10, 0.28)
        du = (xs[None, :] - cu) / sx
        dv = (ys[:, None] - cv) / sy
        mottle += np.exp(-(du * du + dv * dv))
    mottle = np.clip(mottle / 6.0, 0.0, 1.0)

    img = col[:, None, :] * (1.0 - 0.10 * mottle[:, :, None]) + \
          _hex_to_rgb("#6A7F94")[None, None, :] * (0.10 * mottle[:, :, None])

    img = np.clip(img, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


if __name__ == "__main__":
    make_sunny_sky_panorama().save("sky_sunny.png")
    make_rainy_sky_panorama().save("sky_rainy.png")
