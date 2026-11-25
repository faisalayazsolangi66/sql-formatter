#!/usr/bin/env python3
"""Format SQL queries (keyword casing and indentation).

Upper- or lower-cases SQL keywords, puts major clauses (SELECT, FROM,
WHERE, GROUP BY, ORDER BY, JOIN, ...) on their own lines, and indents
continuation lines. Reads from a file, an argument, or stdin.
"""
import argparse
import re
import sys

KEYWORDS = [
    "SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
    "LIMIT", "OFFSET", "JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN",
    "INNER JOIN", "OUTER JOIN", "CROSS JOIN", "ON", "AND", "OR",
    "UNION", "UNION ALL", "INSERT INTO", "VALUES", "UPDATE", "SET",
    "DELETE FROM", "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
]
# Longest first so "LEFT JOIN" wins over "JOIN".
KEYWORDS.sort(key=len, reverse=True)
MAJOR = {"SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
         "LIMIT", "OFFSET", "UNION", "UNION ALL", "INSERT INTO",
         "VALUES", "UPDATE", "SET", "DELETE FROM", "CREATE TABLE",
         "ALTER TABLE", "DROP TABLE"}


def format_sql(sql, case, indent):
    """Format one SQL string; case is 'upper', 'lower' or 'keep'."""
    sql = re.sub(r"\s+", " ", sql).strip()
    if not sql.endswith(";"):
        sql += ";"

    def case_kw(word):
        if case == "upper":
            return word.upper()
        if case == "lower":
            return word.lower()
        return word

    # Protect string literals from keyword rewriting.
    literals = {}

    def stash(match):
        key = f"__STR{len(literals)}__"
        literals[key] = match.group(0)
        return key

    sql = re.sub(r"'(?:[^']|'')*'", stash, sql)

    for keyword in KEYWORDS:
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b",
                             re.IGNORECASE)
        sql = pattern.sub(lambda m, k=keyword: case_kw(k), sql)

    pad = " " * indent
    # Major clauses start a new line; AND/OR/JOIN get a new indented line.
    for keyword in sorted(MAJOR, key=len, reverse=True):
        kw = case_kw(keyword)
        sql = re.sub(r"\s*\b" + re.escape(kw) + r"\b",
                     "\n" + kw, sql, flags=re.IGNORECASE)
    for keyword in ("AND", "OR", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN",
                    "INNER JOIN", "OUTER JOIN", "CROSS JOIN", "JOIN", "ON"):
        kw = case_kw(keyword)
        sql = re.sub(r"\s*\b" + re.escape(kw) + r"\b",
                     "\n" + pad + kw, sql, flags=re.IGNORECASE)

    lines = []
    for line in sql.split("\n"):
        line = line.strip()
        if not line:
            continue
        if not any(line.upper().startswith(case_kw(k).upper())
                   for k in MAJOR) and not line.startswith(pad):
            # Continuation of the previous clause: indent it.
            if lines:
                line = pad + line
        lines.append(line)
    out = "\n".join(lines)
    for key, value in literals.items():
        out = out.replace(key, value)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Format SQL queries (keyword casing and indentation).")
    parser.add_argument("sql", nargs="?",
                        help="SQL query to format (omit to read stdin or --file)")
    parser.add_argument("--file", help="Read SQL from a file")
    parser.add_argument("--case", choices=["upper", "lower", "keep"],
                        default="upper",
                        help="Keyword casing (default: upper)")
    parser.add_argument("--indent", type=int, default=4,
                        help="Spaces per indent level (default: 4)")
    parser.add_argument("--output", help="Write the result to a file")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                sql = fh.read()
        except OSError as exc:
            print(f"Error: cannot read file: {exc}", file=sys.stderr)
            return 1
    elif args.sql:
        sql = args.sql
    elif not sys.stdin.isatty():
        sql = sys.stdin.read()
    else:
        print("Error: provide SQL as an argument, --file, or via stdin",
              file=sys.stderr)
        return 1

    if not sql.strip():
        print("Error: empty SQL input", file=sys.stderr)
        return 1

    formatted = format_sql(sql, args.case, args.indent)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(formatted + "\n")
        print(f"Formatted SQL written to {args.output}")
    else:
        print(formatted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
