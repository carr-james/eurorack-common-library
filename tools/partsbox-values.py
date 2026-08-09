#!/usr/bin/env python3
"""Regenerate docs/preferred-values.md from PartsBox.

Usage: PARTSBOX_KEY=$(cat ~/.tokens/partsbox) tools/partsbox-values.py
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

API = "https://api.partsbox.com/api/1/part/all"
OUT = Path(__file__).resolve().parent.parent / "docs" / "preferred-values.md"

MULTIPLIER = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "mu": 1e-6, "µ": 1e-6}
MECHANICAL_HINTS = ("knob", "header", "socket", "shrouded", "jack", "bracket",
                    "screw", "standoff", "rail", "panel")


def fetch_parts(key):
    request = urllib.request.Request(
        API,
        data=b"",
        headers={"Authorization": f"APIKey {key}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        body = json.load(response)
    if body.get("partsbox.status/category") != "ok":
        sys.exit(f"PartsBox error: {body.get('partsbox.status/message')}")
    return body["data"]


def resistor_ohms(description):
    match = re.search(r"([\d.]+)\s*ohm", description, re.I)
    if match and "resistor" in description.lower():
        return float(match.group(1))
    return None


def capacitor_farads(description):
    match = re.search(r"([\d.]+)\s*(p|n|mu|u|µ)F", description, re.I)
    if match and "cap" in description.lower():
        return float(match.group(1)) * MULTIPLIER[match.group(2).lower()]
    return None


def format_ohms(value):
    for scale, suffix in ((1e6, "M"), (1e3, "k"), (1, "R")):
        if value >= scale:
            return f"{value / scale:g}{suffix}"
    return f"{value:g}R"


def format_farads(value):
    for scale, suffix in ((1e-6, "uF"), (1e-9, "nF"), (1e-12, "pF")):
        if value >= scale:
            return f"{value / scale:g}{suffix}"
    return f"{value:g}F"


def split_remainder(parts):
    actives, mechanical = [], []
    for part in parts:
        description = part.get("part/description") or ""
        if resistor_ohms(description) or capacitor_farads(description):
            continue
        haystack = f"{part['part/name']} {description}".lower()
        target = mechanical if any(h in haystack for h in MECHANICAL_HINTS) else actives
        target.append(part["part/name"])
    return sorted(set(actives)), sorted(set(mechanical))


def render(resistors, capacitors, semiconductors, mechanical):
    return f"""# Preferred values

Generated from PartsBox by `tools/partsbox-values.py`. Do not edit by hand.

PartsBox records which parts are in stock. It does not record how many. Stock
counts there are not maintained, so this file lists presence only.

The list holds most of the stock, not all of it. A value that is absent may
still exist. Treat the list as advice, not as a rule.

## How to choose

1. Choose a value from this file.
2. If the value is not here, choose SMD and buy it.

Passives are well stocked. If a passive value is here, use it freely.

Semiconductors are not. A part here may be a single unit. Prototype with it. If
you want to build the module more than once, check that you can buy the part
again first.

## Resistors

Through hole, metal film, 0.25W, 1%.

{resistors}

## Capacitors

Through hole. Film, ceramic C0G, and aluminium electrolytic.

{capacitors}

## Semiconductors and other actives

Quantities unknown. See "How to choose".

{semiconductors}

## Mechanical and connectors

{mechanical}
"""


def columns(values, per_row=8):
    rows = [values[i:i + per_row] for i in range(0, len(values), per_row)]
    return "\n".join("| " + " | ".join(row.ljust(6) for row in chunk) + " |"
                     for chunk in rows)


def main():
    key = os.environ.get("PARTSBOX_KEY")
    if not key:
        sys.exit("Set PARTSBOX_KEY. See the module docstring.")

    parts = fetch_parts(key.strip())
    ohms, farads = set(), set()
    for part in parts:
        description = part.get("part/description") or ""
        value = resistor_ohms(description)
        if value:
            ohms.add(value)
        value = capacitor_farads(description)
        if value:
            farads.add(value)

    active_names, mechanical_names = split_remainder(parts)
    OUT.write_text(render(
        "\n".join(f"- {format_ohms(v)}" for v in sorted(ohms)),
        "\n".join(f"- {format_farads(v)}" for v in sorted(farads)),
        "\n".join(f"- {n}" for n in active_names),
        "\n".join(f"- {n}" for n in mechanical_names),
    ))
    print(f"{OUT}: {len(ohms)} resistors, {len(farads)} capacitors, "
          f"{len(active_names)} actives, {len(mechanical_names)} mechanical")


if __name__ == "__main__":
    main()
