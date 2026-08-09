#!/usr/bin/env bash
# Rebuild $KICAD10_SYMBOL_DIR after a KiCad upgrade.
#
# Konnect resolves Lib:Symbol as $KICAD10_SYMBOL_DIR/Lib.kicad_sym and ignores
# sym-lib-table, so shared libraries must exist there as files. This farm holds
# symlinks to KiCad's stock libraries plus this one.
set -euo pipefail

FARM="${KICAD10_SYMBOL_DIR:-$HOME/.local/share/kicad10-symbols}"
STOCK="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
SHARED="$(cd "$(dirname "$0")/.." && pwd)/symbols/eurorack-common.kicad_sym"

[ -d "$STOCK" ] || { echo "No stock symbols at $STOCK"; exit 1; }

rm -rf "$FARM"
mkdir -p "$FARM"

for f in "$STOCK"/*.kicad_sym; do
    ln -sf "$f" "$FARM/$(basename "$f")"
done
ln -sf "$SHARED" "$FARM/Eurorack Common.kicad_sym"

echo "$FARM: $(find "$FARM" -type l | wc -l | tr -d ' ') libraries"
