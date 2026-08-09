#!/usr/bin/env python3
"""Download a coloured WRL model from KiCad's upstream 3D package repository.

KiCad's installer ships STEP only. STEP has no colour, so renders come out grey.
The upstream repository still publishes the WRL files that the installer drops.

Usage: tools/fetch-wrl.py Diode_THT.3dshapes/D_DO-41_SOD81_P7.62mm_Horizontal
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/KiCad/kicad-packages3D/master"
DEST = Path(__file__).resolve().parent.parent / "3dmodels"


def fetch(model_path):
    name = Path(model_path).name
    if not name.endswith(".wrl"):
        model_path, name = f"{model_path}.wrl", f"{name}.wrl"

    url = f"{BASE}/{model_path}"
    try:
        with urllib.request.urlopen(url) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        sys.exit(f"{url}\n  HTTP {error.code}. Check the library and model name.")

    if b"diffuseColor" not in body:
        sys.exit(f"{name} has no colour data. Do not use it.")

    out = DEST / name
    out.write_bytes(body)
    colours = body.count(b"diffuseColor")
    print(f"{out}  ({len(body)} bytes, {colours} colours)")
    print(f'  (model "${{KIPRJMOD}}/../shared/3dmodels/{name}")')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fetch(sys.argv[1])
