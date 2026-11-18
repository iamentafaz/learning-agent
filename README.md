# Personal Learning Agent

A daily 30-minute email lesson that combines:

- three English words, with spaced revision;
- Class 10 maths, progressing from the fundamentals;
- a short original brain-stimulating story or puzzle.

## Design

The OpenAI model acts as a teacher. Python code controls the curriculum, progress state, content selection, validation and email delivery. This keeps the agent predictable, low-cost and easy to improve.

The first version generates a daily lesson on demand or through a scheduler. Run it locally first; later deploy the same command to a daily cron job.

## Setup

```bash
cd personal-learning-agent
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e .
cp .env.example .env
```

Fill in `.env`. For Gmail, turn on two-step verification and create an **App Password**; do not use your normal Gmail password.

## Commands

```bash
# Create the SQLite database and seed the first content pack
learning-agent init

# Generate an email preview without sending it
learning-agent generate --dry-run

# Generate and send today's email
learning-agent generate --send
```

Preview HTML is saved in `output/`. The database is `learning.db`.

## Daily scheduler

After local testing, schedule this command once each evening (for example, 8:00 PM IST):

```bash
learning-agent generate --send
```

Use a cron job, GitHub Actions, Render Cron Job, Railway, or a small VPS. Keep all secrets in the host's secret manager, not in the repository.

## Before production

1. Add your recipient email and SMTP credentials.
2. Replace the starter content with a larger reviewed pack.
3. Review generated lessons for the first week.
4. Add an answer/feedback link in Phase 2, so difficulty adapts from your quiz results.

## Local browser UI

Run `learning-agent serve` to open a local browser app for browsing saved lesson previews and generating today's lesson. It binds to `127.0.0.1` and does not require email settings. Keep the terminal open while using it; press Ctrl+C to stop.

## n8n daily workflow

The importable workflow at `n8n/daily-learning-workflow.json` runs daily at 8:00 PM IST. It reads a science RSS feed and a word-of-the-day feed, passes recent entries to this agent, then sends the generated HTML lesson through n8n SMTP. The agent keeps control of the maths sequence, lesson schema, SQLite progress, and saved lesson files; n8n controls scheduling, RSS, and delivery.

1. Set `LEARNING_AGENT_API_TOKEN` in `.env` to a long random value. Keep the existing OpenAI key in `.env`; do not put it in the n8n workflow.
2. Start the API from this project directory in PowerShell:

   ```powershell
   .\.venv\Scripts\learning-agent.exe api
   ```

   Keep that terminal open. The API listens on port 8766 for Docker access. It requires the bearer token and limits RSS payloads; the `/health` route can be used for a local availability check.
3. Import `n8n/daily-learning-workflow.json` into n8n. Edit **Generate Lesson** and replace `REPLACE_WITH_LEARNING_AGENT_API_TOKEN` with the same token. The URL uses `host.docker.internal`, which lets Docker Desktop containers reach a service on the Windows host.
4. In **Email Daily Lesson**, choose your SMTP credential and set the sender and recipient addresses. Replace either RSS URL if you prefer other sources.
5. Run the workflow manually once and inspect the execution and email. Then activate it for the daily schedule.

The API generates at most one lesson per calendar day, matching the existing database guard. Keep the API reachable only on your trusted local network; do not forward port 8766 to the public internet. If n8n is on another machine or Docker host, replace `host.docker.internal` with a private, reachable host address and protect that connection accordingly.
