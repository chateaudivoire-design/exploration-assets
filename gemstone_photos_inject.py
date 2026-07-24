#!/usr/bin/env python3
"""
Gemstone Photo Base64 Injector
Scans for Gemstone-[Cut]-[Color].webp files, base64-encodes them,
and injects a GEM_PHOTO_B64 JavaScript object into index.html.
"""

import os
import base64
import re
import sys

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ CONFIGURATION                                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

CUTS = ['Round', 'Cushion', 'Princess', 'Radiant', 'Emerald', 'Oval', 'Heart', 'Pear']
GEM_COLORS = [
    'Garnet', 'Amethyst', 'Aquamarine', 'Diamond', 'Emerald', 'Alexandrite',
    'Ruby', 'Peridot', 'Sapphire', 'Tourmaline', 'Citrine', 'Tanzanite'
]

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ MAIN LOGIC                                                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def main():
    # Get the directory of this script (should be repo root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(script_dir, 'index.html')

    if not os.path.exists(html_file):
        print(f"ERROR: {html_file} not found")
        sys.exit(1)

    # Scan for webp files matching Gemstone-[Cut]-[Color].webp pattern
    photo_b64 = {}
    found_count = 0
    missing_count = 0

    for cut in CUTS:
        for color in GEM_COLORS:
            filename = f'Gemstone-{cut}-{color}.webp'
            filepath = os.path.join(script_dir, filename)

            if os.path.exists(filepath):
                try:
                    with open(filepath, 'rb') as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode('ascii')
                    # Key format: CutName_ColorName (matching requirement)
                    key = f'{cut}_{color}'
                    photo_b64[key] = b64
                    found_count += 1
                    print(f"  ✓ {filename} ({len(data)} bytes, {len(b64)} chars b64)")
                except Exception as e:
                    print(f"  ✗ {filename} — error reading: {e}")
            else:
                missing_count += 1

    # Build the JavaScript object
    js_lines = ['const GEM_PHOTO_B64 = {']
    keys = sorted(photo_b64.keys())
    for i, key in enumerate(keys):
        b64_str = photo_b64[key]
        comma = ',' if i < len(keys) - 1 else ''
        # Wrap long base64 strings at ~80 chars for readability
        if len(b64_str) > 80:
            # Break into ~80-char chunks
            chunks = [b64_str[j:j+80] for j in range(0, len(b64_str), 80)]
            js_lines.append(f'  "{key}":')
            for chunk_idx, chunk in enumerate(chunks):
                if chunk_idx == len(chunks) - 1:
                    js_lines.append(f'    "{chunk}"{comma}')
                else:
                    js_lines.append(f'    "{chunk}" +')
        else:
            js_lines.append(f'  "{key}": "{b64_str}"{comma}')

    js_lines.append('};')
    js_object = '\n'.join(js_lines)

    # Read the current index.html
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find and replace or insert the GEM_PHOTO_B64 block
    # Pattern: const GEM_PHOTO_B64 = { ... };
    pattern = r'const GEM_PHOTO_B64\s*=\s*\{[^}]*\};'
    if re.search(pattern, html_content, re.DOTALL):
        # Replace existing block
        html_content = re.sub(pattern, js_object, html_content, count=1, flags=re.DOTALL)
        action = 'replaced'
    else:
        # Insert before const GEM_COLORS
        colors_pattern = r'(const GEM_COLORS\s*=\s*\[)'
        if re.search(colors_pattern, html_content):
            html_content = re.sub(colors_pattern, f'{js_object}\n\n\\1', html_content, count=1)
            action = 'inserted (before GEM_COLORS)'
        else:
            print("ERROR: Could not find GEM_COLORS in index.html — cannot inject GEM_PHOTO_B64")
            sys.exit(1)

    # Write back the modified HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Print summary
    total_combinations = len(CUTS) * len(GEM_COLORS)
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║ GEMSTONE PHOTO INJECTION COMPLETE                          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"  Found:       {found_count:3d}/{total_combinations} combinations")
    print(f"  Missing:     {missing_count:3d}/{total_combinations} combinations")
    print(f"  Action:      {action}")
    print(f"  File:        {html_file}")
    print()

if __name__ == '__main__':
    main()
