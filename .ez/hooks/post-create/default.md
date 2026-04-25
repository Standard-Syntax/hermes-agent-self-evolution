# Worktree Setup

After creating this worktree:

## 1. Re-anchor

```bash
pwd
git rev-parse --show-toplevel
ez status --json
````

## 2. Install Dependencies

Install dependencies using the repo's package manager.

Examples:

```bash
npm install
# or
pnpm install
# or
uv sync
```

## 3. Copy Local Environment Files

Copy local env files only if required by the repo:

```bash
cp .env.example .env
```

## 4. Use the Worktree Port

Use `$EZ_PORT` for any dev server started from this worktree.

Example:

```bash
npm run dev -- --port "$EZ_PORT"
```

## 5. Before Pushing

Always run:

```bash
ez diff --stat
ez diff --name-only
ez sync --autostash
```

