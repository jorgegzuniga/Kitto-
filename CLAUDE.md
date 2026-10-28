# cad — notes for Claude

Code-CAD repo for Jorge's 3D printing projects, worked on mostly from his phone.

## Layout
- `models/<project>/<part>.py` — one printable part per file, written in build123d. Each file must define a variable `part`. Files starting with `_` are helpers and aren't rendered.
- `models/<project>/README.md` — the project's requirements and decisions. Read it before changing a part, and update it when Jorge decides something.
- `out/<project>/` — generated STL, 3MF and a 3-view preview PNG per part. Never edit by hand.
- `tools/render.py` — builds everything: `python tools/render.py [project-filter]`.

## Working loop
1. Edit or add the part script. Keep every dimension a named variable at the top of the file, in mm.
2. Run `python tools/render.py <project>` and look at the preview PNG yourself before reporting back. Check the printed size line is what you intended.
3. Show Jorge the preview image, then commit and push to `main`. The GitHub Action re-renders and commits `out/`, so the STL opens in GitHub's 3D viewer on his phone.

## Printing context
- Printers: Bambu Lab A1, A1 mini, one more Bambu, and a Snapmaker U1 (multi-material). Slices in OrcaSlicer.
- Design for FDM: flat base on the bed, avoid overhangs past ~45°, 0.2–0.3 mm clearance for press/slide fits, walls at least 1.2 mm.
- Mesh models (Meshy output, downloaded STLs) live in `meshes/` and can only take simple edits (scale, cut, booleans), not reshaping.
