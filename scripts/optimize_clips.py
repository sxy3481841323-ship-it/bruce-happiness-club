#!/usr/bin/env python3
"""Optimize raw AI-generated MP4 clips from assets/clips_raw/<scene_id>/ into
WeChat-friendly 720p H.264 MP4s under assets/clips/<scene_id>/ (<= 1.2 MB target).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "assets" / "clips_raw"
OUT_DIR = ROOT / "assets" / "clips"
TARGET_BYTES = int(1.2 * 1024 * 1024)


def run_ffmpeg(ffmpeg_bin: str, src: Path, dst: Path, crf: int) -> None:
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(src),
        "-vf",
        "scale=-2:720:flags=lanczos,fps=30",
        "-c:v",
        "libx264",
        "-profile:v",
        "main",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        str(crf),
        "-preset",
        "slow",
        "-movflags",
        "+faststart",
        "-an",
        str(dst),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> int:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        print("未检测到 ffmpeg，无法自动转码压缩视频。")
        print("建议先运行安装：")
        print("  brew install ffmpeg")
        print("或使用剪映等工具手动导出为 720p / 30fps / H.264 MP4（建议单段 <= 1.2 MB），")
        print(f"然后直接放进 {OUT_DIR}/<场景ID>/ 目录（如 intro.mp4、win.mp4、fail_phone.mp4、fail_hazard.mp4）。")
        return 0

    if not RAW_DIR.exists():
        print(f"未找到原始视频目录：{RAW_DIR}")
        print("请先按 PRODUCTION_BRIEF.md 把可灵/即梦生成的原片放入 assets/clips_raw/<场景ID>/ 后再运行本脚本。")
        return 0

    raw_files = sorted(RAW_DIR.rglob("*.mp4"))
    if not raw_files:
        print(f"{RAW_DIR} 下暂无 .mp4 原片。放入后重新运行 python3 scripts/optimize_clips.py 即可。")
        return 0

    for src in raw_files:
        rel = src.relative_to(RAW_DIR)
        dst = OUT_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        in_size = src.stat().st_size
        run_ffmpeg(ffmpeg_bin, src, dst, crf=28)
        out_size = dst.stat().st_size
        used_crf = 28
        if out_size > TARGET_BYTES:
            run_ffmpeg(ffmpeg_bin, src, dst, crf=31)
            out_size = dst.stat().st_size
            used_crf = 31
        print(
            f"[OK] {rel} (crf={used_crf}): "
            f"{in_size / (1024 * 1024):.2f} MB -> {out_size / (1024 * 1024):.2f} MB"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
