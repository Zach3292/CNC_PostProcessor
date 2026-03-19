import os
from pathlib import Path
# Get all .NC files in the current directory
nc_files = Path('.').glob('*.NC')

for file in nc_files:
    content = ""
    with open(file, 'r') as f:
        content = f.readlines()
        print(f"Processing {file}")
    
    program_start = False
    formatted_content = ["G90\n", "M5\n", "G53 Z0\n"]  # Start with absolute positioning, stop spindle, and move to machine home

    for line in content:
        if line.strip().startswith('%') or \
            line.strip().startswith('(') or \
            not line.strip() or \
            line.strip().startswith('T') or \
            line.strip().startswith('O') or \
            line.strip().startswith('G43') or \
            line.strip().startswith('G49') or \
            line.strip().startswith('G269') or \
            line.strip().startswith('G91') or \
            line.strip().startswith('G28') or \
            line.strip().startswith('G43') or \
            line.strip().startswith('M30') or \
            not program_start:
            if line.strip().startswith('S'):
                program_start = True  # Start processing after the first O command
            else:
                continue  # Skip comment lines

        if '( Setup )' in line:
            continue

        if line.strip().startswith('M5'):
            formatted_content.append("G53 Z0\n")
        
        if line.strip().startswith('S'):
            splitted_line = line.split();
            formatted_content.append(splitted_line[0] + "\n")
            formatted_content.append(splitted_line[1] + "\n")
            formatted_content.append("G53 Z0\n")
        else:
            formatted_content.append(line)

    # Ensure every line starts with a G command by copying the last modal G command
    import re
    last_g_command = None
    for i, line in enumerate(formatted_content):
        stripped = line.strip()
        # Check if line starts with a modal G command (G0, G1, G2, G3)
        g_match = re.match(r'(G[0-3])\b', stripped)
        if g_match:
            last_g_command = g_match.group(1)
        # If line starts with a coordinate (X, Y, Z, I, J, K, F) without a G command, prepend the last one
        elif last_g_command and re.match(r'[XYZIJKF]', stripped):
            formatted_content[i] = last_g_command + " " + line.lstrip()

    new_file_name = file.stem + "_formatted.tap"
    with open(new_file_name, 'w') as f:
        f.writelines(formatted_content)
    print(f"Formatted file saved as {new_file_name}")
