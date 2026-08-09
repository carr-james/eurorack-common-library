# Eurorack Common Library

Shared foundations for the Eurorack projects: parts, design rules, and the
values held in stock.

Every module project already pins this repo as a submodule at
`hardware/shared`, so anything here is available to all of them without extra
wiring.

Circuits live in
[eurorack-blocks](https://github.com/carr-james/eurorack-blocks). Boards live in
[eurorack-breakouts](https://github.com/carr-james/eurorack-breakouts).

Requires KiCad 10.

## Contents

```
symbols/        eurorack-common.kicad_sym
footprints/     eurorack-common.pretty
3dmodels/       STEP and WRL models
spice/          simulation models
design-rules/   house-mill.kicad_dru
docs/           preferred-values.md
tools/          partsbox-values.py
```

## Use in a project

Add the repo as a submodule at `hardware/shared`. Point the project library
tables at it:

```
(lib (name "Eurorack Common")(type "KiCad")
     (uri "${KIPRJMOD}/../shared/symbols/eurorack-common.kicad_sym"))
```

Paths stay project-relative, so a project works on any machine with no global
KiCad configuration.

## 3D models: why footprints are vendored

Many footprints here duplicate a stock KiCad footprint. This is deliberate. Do
not replace them with the stock version.

KiCad 10 ships 7245 STEP models and no WRL models. STEP holds geometry but no
colour. A footprint that points at a stock model therefore renders grey, and
KiBot reports `(W174) Missing WRL 3D model for ... colors`.

Each footprint here points at a WRL file in `3dmodels/` instead:

```
(model "${KIPRJMOD}/../shared/3dmodels/<name>.wrl")
```

This gives two things:

- Colour in `render_3d` and Blender output.
- A project-relative path. The model resolves in CI containers and on any
  machine. Stock footprints use `${KICAD10_3DMODEL_DIR}`, which fails when the
  variable is absent or names an older KiCad version.

When you add a part, add its footprint here and give it a WRL model. A STEP
file alone renders without colour.

### How to make a WRL model

Route 1 — KiCad ships a STEP for the part. Convert it with **kicad StepUp**, a
FreeCAD workbench. StepUp writes the vertices at KiCad scale, so the footprint
keeps `(scale 1 1 1)`. 16 models here came this way.

Route 2 — KiCad ships nothing. Find a model from the vendor or a CAD library,
then convert it to VRML. 7 models here came this way, all Eurorack or vendor
parts: the Alpha pot, Thonkicon jack, shrouded header, SPDT switch, both Bourns
trimmers, and the TI TSOT package. These arrive in mm, so the footprint scales
them down.

Route 3 — you need a variant. Modify the model in FreeCAD first, then convert.
`Potentiometer_Bourns_3296W_Horizontal` is one: the legs are bent 90 degrees so
the trimmer lies flat.

Scale down by **0.3937** (1/2.54), not 0.4. The 8 footprints that use 0.4 render
1.6 percent oversize. This affects renders only, not fabrication.

### Known gaps

- `LED_D3.0mm_Extended10mm` and `LED_D3.0mm_Extended5mm` have no WRL pair. They
  render without colour.
- 8 footprints use `(scale 0.4)`. Correct value is 0.3937.

## Design rules

`design-rules/house-mill.kicad_dru` holds the default rules. They target the
Makera Carvera Air.

| | Mill | JLCPCB |
|---|---|---|
| Track and clearance | 0.2mm | 0.127mm |
| Via | 0.9mm, unplated | 0.3mm, plated |
| Layers | 2 | 4 or more |

Mill rules are stricter, so a board that obeys them is also fabbable at JLCPCB.
The opposite is not true.

Copy the file next to a board as `<project>.kicad_dru`. Raise the Board Setup
minimums to match. Custom rules can tighten the built-in constraints but cannot
loosen them.

## Preferred values

`docs/preferred-values.md` lists the values held in stock. Choose from it
first. If a value is absent, choose SMD and buy it.

Regenerate the file when stock changes:

```bash
PARTSBOX_KEY=$(cat ~/.tokens/partsbox) tools/partsbox-values.py
```

PartsBox records which parts are in stock, not how many. The file lists presence
only. It holds most of the stock, not all. Treat it as advice.
