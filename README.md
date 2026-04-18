# envpatch

> CLI tool to diff and sync `.env` files across environments safely.

---

## Installation

```bash
pip install envpatch
```

Or with pipx:

```bash
pipx install envpatch
```

---

## Usage

Compare two `.env` files and see what's different:

```bash
envpatch diff .env.local .env.production
```

Sync missing keys from one file into another:

```bash
envpatch sync .env.example .env.local
```

Apply a patch file to update an existing `.env`:

```bash
envpatch apply changes.patch .env.local
```

### Example Output

```
[+] NEW_API_KEY       present in source, missing in target
[~] DATABASE_URL      value differs between environments
[-] LEGACY_TOKEN      present in target, missing in source
```

Use `--dry-run` to preview changes without writing to disk:

```bash
envpatch sync .env.example .env.local --dry-run
```

---

## Options

| Flag         | Description                          |
|--------------|--------------------------------------|
| `--dry-run`  | Preview changes without applying     |
| `--quiet`    | Suppress output, exit code only      |
| `--no-color` | Disable colored terminal output      |

---

## License

MIT © [envpatch contributors](https://github.com/your-org/envpatch)