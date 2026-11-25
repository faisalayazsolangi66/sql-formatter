# sql-formatter

Format SQL queries: keyword casing and indentation, with major clauses on their own lines.

## Requirements

- Python 3 (standard library only — no third-party packages)

## How to run

```bash
cd 059-sql-formatter
python3 main.py "select id, name from users where active = 1 order by name"
```

Run `python3 main.py --help` to see all options.

## Example

```bash
python3 main.py "select id, name from users where active = 1 order by name"
```

Sample output:

```
SELECT id, name
FROM users
WHERE active = 1
ORDER BY name;
```

## Notes

Reads SQL from an argument, `--file`, or stdin. Use `--case lower|keep` for keyword casing, `--indent N` for spaces per level, and `--output` to write the result to a file.

## License

MIT — see [LICENSE](LICENSE).
