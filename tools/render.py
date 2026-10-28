"""Build every model in models/ and write STL, 3MF and preview PNGs to out/.

Each models/<project>/<part>.py must define `part` (a build123d Part/Compound).
Usage: python tools/render.py            # all models
       python tools/render.py keychain   # only projects whose name contains "keychain"
"""
import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from build123d import Mesher, export_stl
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh as stlmesh

ROOT = Path(__file__).resolve().parent.parent
MODELS, OUT = ROOT / "models", ROOT / "out"
VIEWS = {"iso": (25, -60), "front": (0, -90), "top": (90, -90)}


def load_part(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "part"):
        raise ValueError(f"{path} does not define `part`")
    return mod.part


def preview(stl_path: Path, png_path: Path):
    m = stlmesh.Mesh.from_file(str(stl_path))
    pts = m.vectors.reshape(-1, 3)
    lo, hi = pts.min(0), pts.max(0)
    size = hi - lo
    fig = plt.figure(figsize=(12, 4.4), dpi=110)
    light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)
    n = m.normals / (np.linalg.norm(m.normals, axis=1, keepdims=True) + 1e-9)
    shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
    colors = np.c_[0.36 * shade, 0.30 * shade + 0.1, 0.85 * shade, np.ones_like(shade)]
    for i, (name, (elev, azim)) in enumerate(VIEWS.items()):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(m.vectors, facecolors=colors, edgecolors=colors, linewidths=0.3))
        c, r = (lo + hi) / 2, size.max() / 2
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1)); ax.view_init(elev, azim); ax.set_axis_off()
        ax.set_title(name, fontsize=10)
    fig.suptitle(f"{stl_path.stem}  —  {size[0]:.1f} × {size[1]:.1f} × {size[2]:.1f} mm", fontsize=11)
    fig.tight_layout()
    fig.savefig(png_path)
    plt.close(fig)


def main(filter_text: str = ""):
    files = sorted(p for p in MODELS.glob("*/*.py") if not p.name.startswith("_"))
    files = [p for p in files if filter_text in p.parent.name]
    if not files:
        sys.exit(f"No models found in {MODELS} matching '{filter_text}'")
    failed = []
    for path in files:
        dest = OUT / path.parent.name
        dest.mkdir(parents=True, exist_ok=True)
        try:
            part = load_part(path)
            stl_path, mf_path = dest / f"{path.stem}.stl", dest / f"{path.stem}.3mf"
            export_stl(part, str(stl_path))
            mesher = Mesher(); mesher.add_shape(part); mesher.write(str(mf_path))
            preview(stl_path, dest / f"{path.stem}.png")
            bb = part.bounding_box()
            print(f"OK   {path.relative_to(ROOT)}  {bb.size.X:.1f}×{bb.size.Y:.1f}×{bb.size.Z:.1f} mm  vol {part.volume:.0f} mm³")
        except Exception as e:  # keep going so one broken part doesn't hide the others
            failed.append(path)
            print(f"FAIL {path.relative_to(ROOT)}: {e}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
