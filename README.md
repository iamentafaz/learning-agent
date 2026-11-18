# Personal Learning Agent

A daily 30-minute email lesson that combines:

- three English words, with spaced revision;
- Class 10 maths, progressing from the fundamentals;
- a short original brain-stimulating story or puzzle.

## How it works

The OpenAI model writes the lesson. The Python application chooses the next Class 10 maths topic, tracks vocabulary reviews in SQLite, validates the lesson structure, and saves JSON and HTML copies. You can use the built-in SMTP command-line delivery or let n8n handle scheduling, RSS collection, and email delivery.

The n8n workflow is a fixed automation: it reads two RSS feeds, calls the agent API, and emails the returned lesson. The API must be running when n8n calls it; n8n does not start the Python server process.

## Setup

Python 3.12 or newer is required. Create a virtual environment, install the project, and copy `.env.example` to `.env`.

**Windows PowerShell:**

```powershell
cd personal-learning-agent
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item .env.example .env
```

**macOS or Linux:**

```bash
cd personal-learning-agent
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env` and choose a model available to your OpenAI API account in `OPENAI_MODEL`. Keep `.env` private; it is excluded by `.gitignore`.

## Commands

Run these from the project directory. On Windows, use:

```powershell
.\.venv\Scripts\python.exe -m learning_agent.cli init
.\.venv\Scripts\python.exe -m learning_agent.cli generate --dry-run
.\.venv\Scripts\python.exe -m learning_agent.cli generate --send
```

On macOS or Linux, use:

```bash
.venv/bin/python -m learning_agent.cli init
.venv/bin/python -m learning_agent.cli generate --dry-run
.venv/bin/python -m learning_agent.cli generate --send
```

Preview HTML is saved in `output/`. The database is `learning.db`.

## Daily scheduler

After local testing, schedule this command once each evening (for example, 8:00 PM IST):

```text
# Windows PowerShell, with the project virtual environment:
.\.venv\Scripts\python.exe -m learning_agent.cli generate --send

# macOS or Linux:
.venv/bin/python -m learning_agent.cli generate --send
```

Use a local scheduler, cron, or a hosted scheduler. Keep `learning.db` and `output/` on persistent storage so review progress and saved lessons survive between runs. Keep all secrets in the host's secret manager, not in the repository.

## Before production

1. Add your recipient email and SMTP credentials.
2. Replace the starter content with a larger reviewed pack.
3. Review generated lessons for the first week.
4. Add an answer/feedback link in Phase 2, so difficulty adapts from your quiz results.

## Local browser UI

Run `.\.venv\Scripts\python.exe -m learning_agent.cli serve` on Windows or `.venv/bin/python -m learning_agent.cli serve` on macOS/Linux to open a local browser app for browsing saved lesson previews and generating today's lesson. It binds to `127.0.0.1` and does not require email settings. Keep the terminal open while using it; press Ctrl+C to stop.

## n8n daily workflow

The importable workflow at `n8n/daily-learning-workflow.json` runs daily at 8:00 PM Asia/Kolkata. It reads a science RSS feed and a word-of-the-day feed, passes up to 12 recent entries from each feed to this agent, then sends the generated HTML lesson through n8n SMTP. The feed items are optional context: the lesson keeps its planned maths curriculum, and RSS vocabulary can replace words that are not due for review.

### 1. Configure the agent API

Set `LEARNING_AGENT_API_TOKEN` in `.env` to a unique random secret. For example, in PowerShell generate a 32-byte URL-safe token with:

```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
$rng.Dispose()
[Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+','-').Replace('/','_')
```

Copy the printed value into `.env` after `LEARNING_AGENT_API_TOKEN=`. Do not use the example placeholder, commit `.env`, or put your OpenAI API key in n8n.

Start the API from the project directory. On Windows, use the virtual environment's Python module command (the generated `.exe` launcher may be blocked by Windows application-control policies):

   ```powershell
   .\.venv\Scripts\python.exe -m learning_agent.cli api
   ```

On macOS or Linux, run `.venv/bin/python -m learning_agent.cli api`. The API listens on port 8766 and requires the bearer token for generation requests. Check `http://127.0.0.1:8766/health` from the host to confirm it is running. Keep the server process running while n8n uses it, and keep the computer awake for scheduled runs.

### 2. Import and configure n8n

1. In n8n, import `n8n/daily-learning-workflow.json` from a file.
2. In **Generate Lesson**, replace `REPLACE_WITH_LEARNING_AGENT_API_TOKEN` with the token from `.env`, prefixed with `Bearer ` (for example, `Bearer your-token`). The template URL is `http://host.docker.internal:8766/api/generate`, which is the usual Docker Desktop route from a container to the Windows or macOS host.
3. In **Email Daily Lesson**, select or create an SMTP credential and set the sender and recipient addresses. For personal Gmail, enable 2-Step Verification and use a Google App Password with `smtp.gmail.com`, port `587`, and STARTTLS. Keep email credentials in n8n's credential store.
4. Review the RSS URLs in **Learning Topics RSS** and **Vocabulary RSS** and replace them with feeds you prefer.
5. Run the workflow once manually and confirm the email arrives. Then activate it to run on the daily schedule.

The API generates at most one new lesson per calendar day. Re-running the workflow can send the saved lesson again. The API binds to all host interfaces so Docker can reach it; keep port 8766 on a trusted private network and do not forward it to the public internet. `host.docker.internal` is provided by Docker Desktop; other Docker setups may need a host-gateway entry or a private host address. If n8n runs on another machine, use a reachable private address and secure that connection.

If the API returns `Connection error` while calling OpenAI, check that the host can reach `api.openai.com:443` and that any `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY` environment settings point to a working proxy. The API process inherits these settings when it starts.
