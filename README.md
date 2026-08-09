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
