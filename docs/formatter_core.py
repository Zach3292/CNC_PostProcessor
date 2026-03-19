import re

SKIP_PREFIXES = (
    "%",
    "(",
    "T",
    "O",
    "G43",
    "G49",
    "G269",
    "G91",
    "G28",
    "M30",
)


def format_nc(content: str) -> str:
    lines = content.splitlines(keepends=True)
    program_start = False

    formatted_content = ["G90\n", "M5\n", "G53 Z0\n"]

    for line in lines:
        stripped = line.strip()

        if (
            not stripped
            or stripped.startswith(SKIP_PREFIXES)
            or not program_start
        ):
            if stripped.startswith("S"):
                program_start = True
            else:
                continue

        if "( Setup )" in line:
            continue

        if stripped.startswith("M5"):
            formatted_content.append("G53 Z0\n")

        if stripped.startswith("S"):
            parts = line.split()
            if len(parts) >= 1:
                formatted_content.append(parts[0] + "\n")
            if len(parts) >= 2:
                formatted_content.append(parts[1] + "\n")
            formatted_content.append("G53 Z0\n")
        else:
            if line.endswith("\n"):
                formatted_content.append(line)
            else:
                formatted_content.append(line + "\n")

    # Ensure every line starts with a G command by copying the last modal G command
    last_g_command = None
    for i, line in enumerate(formatted_content):
        stripped = line.strip()
        # Check if line starts with a modal G command (G0, G1, G2, G3)
        g_match = re.match(r'(G[0-3])\b', stripped)

        if g_match:
            last_g_command = g_match.group(1)
        # If line starts with a coordinate (X, Y, Z, I, J, K, F) without a G command, prepend the last one
        elif last_g_command and re.match(r"[XYZIJKF]", stripped):
            formatted_content[i] = last_g_command + " " + line.lstrip()

    return "".join(formatted_content)


def make_output_filename(input_filename: str) -> str:
    if not input_filename:
        return "formatted.tap"

    dot_index = input_filename.rfind(".")
    if dot_index == -1:
        stem = input_filename
    else:
        stem = input_filename[:dot_index]

    return stem + "_formatted.tap"
