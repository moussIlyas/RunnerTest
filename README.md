# Dockerized self-hosted GitHub Actions runner + Python CI demo

This folder contains everything needed to turn this Fedora machine into a
GitHub Actions **self-hosted runner** running inside Docker, plus a tiny Python
project used to prove that the setup works end to end.

```
.
├── calculator.py                     # demo code
├── tests/test_calculator.py          # pytest unit tests
├── pyproject.toml                    # pytest configuration
├── requirements-dev.txt              # dev dependencies (pytest)
├── .github/workflows/ci.yml          # workflow that runs on the self-hosted runner
└── runner/
    ├── Dockerfile                    # runner image (adds a Python sanity check)
    ├── docker-compose.yml            # runner service definition
    ├── .env.example                  # template for REPO_URL + ACCESS_TOKEN
    └── manage.sh                     # up / down / restart / logs / status helper
```

The runner container uses the well-known
[`myoung34/github-runner`](https://github.com/myoung34/docker-github-actions-runner)
image (Ubuntu 26.04 base). It already ships Python 3.14, pip, venv, git, jq,
curl and gcc, so the Python workflow runs without extra installation.

---

## Part 1 — What I need from GitHub (step by step)

I cannot finish the registration without a **repository** and a **token**.
Please do the following and send me the two values.

### Step 1. Create (or pick) the repository

Create an empty repository on GitHub, e.g. `YOUR_USER/gha-runner-demo`.

- **Keep it private.** Self-hosted runners execute code on this machine; never
  run untrusted pull requests from a public repository on them.
- You must have **admin** rights on the repository to register a runner.

### Step 2. Create a token that can register runners

GitHub offers two token types; either works.

**Option A — Fine-grained token (recommended)**

1. Click your avatar → **Settings**.
2. **Developer settings** → **Personal access tokens** → **Fine-grained tokens**.
3. **Generate new token**.
4. Fill in:
   - **Token name:** `fedora-self-hosted-runner`
   - **Expiration:** e.g. 90 days
   - **Resource owner:** your user (or the organization that owns the repo)
   - **Repository access:** *Only select repositories* → pick your repo
   - **Repository permissions → Administration:** **Read and write**
     (`Metadata: Read-only` is added automatically)
5. **Generate token** and copy the `github_pat_...` value.

**Option B — Classic token**

1. **Settings** → **Developer settings** → **Personal access tokens (classic)**
   → **Generate new token (classic)**.
2. Select the **`repo`** scope (for an organization runner also `admin:org`).
3. Copy the `ghp_...` value.

> The token is a password. Do **not** paste it into a chat, an issue, or a
> commit. Put it in `runner/.env`, which is already excluded by `.gitignore`.

### Step 3. (Organization runners only)

If you want the runner registered on an **organization** instead of a single
repository:

- The organization must allow self-hosted runners
  (**Organization settings → Actions → Runners**).
- The token needs **Organization permissions → Self-hosted runners: Read and write**
  (fine-grained) or `admin:org` (classic).
- I will set `RUNNER_SCOPE=org` and `ORG_NAME=...` instead of `REPO_URL`.

### Step 4. Give me these two values

```
REPO_URL=https://github.com/<owner>/<repo>
ACCESS_TOKEN=github_pat_...
```

Either paste them into `runner/.env` yourself (see Part 2) or tell me and I will
put them in place and start the runner.

---

## Part 2 — Start the runner (2 commands)

```bash
cd runner
cp .env.example .env
$EDITOR .env          # set REPO_URL and ACCESS_TOKEN
./manage.sh up        # docker compose up -d --build
./manage.sh logs      # watch the registration
```

A healthy start looks like this in the logs:

```
--------------------------------------------------------------------------------
|        ____ _ _   _   _       _          _        _   _                      |
|       / ___(_) |_| | | |_   _| |__      / \   ___| |_(_) ___  _ __  ___      |
...
√ Connected to GitHub
...
√ Runner successfully added
√ Runner connection is good
Listening for Jobs
```

Then verify in GitHub:

**Repository → Settings → Actions → Runners**

You should see `fedora-docker-runner` with a green **Idle** dot and the labels
`self-hosted`, `Linux`, `X64`, `python`.

Useful commands:

| Command              | What it does                                          |
| -------------------- | ----------------------------------------------------- |
| `./manage.sh status` | Show the container state                             |
| `./manage.sh logs`   | Follow runner logs                                   |
| `./manage.sh restart`| Restart the container                                |
| `./manage.sh down`   | Stop container and deregister the runner from GitHub |

The container restarts automatically after a reboot (`restart: unless-stopped`,
and the Docker service is already enabled on this machine).

---

## Part 3 — Push the demo project and watch CI run

```bash
cd /home/moussl/PycharmProjects/PythonProject
git init -b main
git add .
git commit -m "Add Python calculator, unit tests and self-hosted CI workflow"
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

Open **Actions → CI → pytest (self-hosted)**. The job starts within seconds
because a runner is already listening; it is not queued for a GitHub-hosted
runner.

What the workflow does:

1. `actions/checkout@v4` clones the repo into the runner's workspace.
2. Creates `.venv` and installs `pytest`.
3. Runs `python -m pytest -v` (17 test cases).
4. Runs a small smoke test importing `calculator.py`.

To verify locally without GitHub:

```bash
cd /home/moussl/PycharmProjects/PythonProject
python3 -m pytest -v
```

---

## Part 4 — How it is wired

`runner/docker-compose.yml`:

- `env_file: .env` supplies `REPO_URL` / `ACCESS_TOKEN` / `RUNNER_NAME` / `RUNNER_LABELS`.
- `RUNNER_SCOPE: repo` registers the runner on one repository.
- `LABELS` (from `RUNNER_LABELS`) adds `python` on top of the automatic
  `self-hosted`, `Linux` and `X64` labels.
- `UNSET_CONFIG_VARS: "true"` removes the PAT from the environment before any
  workflow step runs, so job code cannot read it.
- `security_opt: label=disable` avoids SELinux denials on Fedora.
- No host directories are mounted: the workspace lives inside the container and
  the machine's files are not exposed to workflows.

The `ACCESS_TOKEN` is only used at container start to obtain a short-lived
runner registration token from the GitHub API. Registration is refreshed on
every container start, so an expired job-level token is not a problem.

### Scaling / organization notes

- One container = one concurrent job. For more parallelism, add replicas with
  `RANDOM_RUNNER_SUFFIX=true` and no fixed `RUNNER_NAME`.
- Do not share `RUNNER_WORKDIR` between replicas.
- For organization scope set `RUNNER_SCOPE=org`, `ORG_NAME=<org>`, drop
  `REPO_URL`.
- If a workflow really needs Docker (`docker build`, service containers), mount
  `/var/run/docker.sock:/var/run/docker.sock` and add the runner user to the
  socket's group; this is **not** enabled by default on purpose.

---

## Part 5 — Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `Bad credentials` / HTTP 401 at start | Token invalid, expired, or lacks **Administration: Read and write** on the repo (or `repo` scope for classic). Generate a new one. |
| Runner never appears in GitHub | Wrong `REPO_URL` (must be the repo URL, no `.git` suffix needed), or the container is crash-looping: `./manage.sh logs`. |
| Job stuck on *Waiting for a runner* | Label mismatch. The job uses `[self-hosted, linux, x64, python]`; check the labels shown on the runner page and in `RUNNER_LABELS`. |
| `permission denied while trying to connect to the Docker daemon` | Your user is in the `docker` group but the shell session is old: log out/in or run `newgrp docker`. |
| SELinux `permission denied` on a bind mount you added | Append `:z` to the volume or keep `security_opt: label=disable`. |
| Container restarts repeatedly | Check `docker compose logs`; the usual causes are a bad token or no network access to `github.com`. |
| Runner is offline after a reboot | `sudo systemctl enable --now docker` (already enabled here), then `docker start gha-runner`. |
| Host feels low on memory | This machine has ~7.6 GB RAM. One idle runner uses ~100 MB; jobs that build large containers need headroom. |

Rotate the token any time by editing `runner/.env` and running
`./manage.sh restart` (the container re-registers automatically).
