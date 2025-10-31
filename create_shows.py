#!/usr/bin/env python3
"""
create_shows.py

Reads a CSV file (hardcoded path below) and creates Show objects for each row.
Implements a minimal CSV parser (no external modules).
"""

CSV_PATH = r"C:\Users\sebas\Downloads\TV_show_data.csv"


def _sanitize_field_name(name):
    """Convert a CSV header name into a safe Python attribute name."""
    name = name.strip()
    out = ''.join(ch if ch.isalnum() or ch == '_' else '_' for ch in name)
    if not out:
        out = 'field'
    if out[0].isdigit():
        out = '_' + out
    return out


def parse_csv_line(line):
    """Parse a single CSV line with quoted fields and escaped quotes."""
    fields, cur, in_quotes = [], [], False
    i, L = 0, len(line)

    while i < L:
        ch = line[i]
        if ch == '"':
            if in_quotes and i + 1 < L and line[i + 1] == '"':
                cur.append('"')  # escaped quote
                i += 1
            else:
                in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(''.join(cur))
            cur.clear()
        else:
            cur.append(ch)
        i += 1

    fields.append(''.join(cur).rstrip('\r\n'))
    return fields


class Show:
    """A simple data container for one TV show record."""

    def __init__(self, field_map):
        self._header_map = field_map.copy()
        for k, v in field_map.items():
            setattr(self, k, v)

    def to_dict(self):
        return {k: getattr(self, k) for k in self._header_map}

    def __repr__(self):
        title = next(
            (getattr(self, attr) for attr in ('title', 'Name', 'TITLE', 'show_title')
             if attr in self.__dict__),
            getattr(self, next(iter(self._header_map), ''), '')
        )
        return f"Show({title!r})"


def load_shows_from_csv(path):
    """Load and parse a CSV file into a list of Show objects."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line for line in f.read().splitlines() if line.strip()]

    if not lines:
        return []

    headers = parse_csv_line(lines[0])
    sanitized_headers = [_sanitize_field_name(h) for h in headers]

    shows = []
    for line in lines[1:]:
        values = parse_csv_line(line)
        # Pad or extend as needed
        if len(values) < len(sanitized_headers):
            values += [''] * (len(sanitized_headers) - len(values))

        field_map = {
            (sanitized_headers[i] if i < len(sanitized_headers)
             else f'extra_{i - len(sanitized_headers) + 1}'): val
            for i, val in enumerate(values)
        }
        shows.append(Show(field_map))
    return shows


if __name__ == '__main__':
    print(f"Reading CSV from: {CSV_PATH}")
    try:
        shows = load_shows_from_csv(CSV_PATH)
    except Exception as e:
        print("Error reading CSV:", e)
    else:
        print(f"Created {len(shows)} show objects.")
        for i, show in enumerate(shows[:5], 1):
            print(f"[{i}] {show.to_dict()}")
        if len(shows) > 5:
            print("... (only first 5 shown)")
