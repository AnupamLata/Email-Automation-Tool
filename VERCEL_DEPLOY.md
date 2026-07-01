# Deploying to Vercel

1. Install the Vercel CLI (optional but helpful):

```bash
npm i -g vercel
```

2. Add required environment variables in the Vercel dashboard or via CLI:

- `EMAIL` — SMTP login email
- `PASSWORD` — SMTP password or app-specific password
- `SMTP_SERVER` — optional (defaults to `smtp.gmail.com`)
- `PORT` — optional (defaults to `587`)

Using the CLI:

```bash
vercel env add EMAIL production
vercel env add PASSWORD production
```

3. Deploy:

```bash
vercel --prod
```

Local testing:

1. Create a `.env` file with the same variables for local runs.
2. Run Vercel dev if you have the CLI:

```bash
vercel dev
```

Notes:
- The site frontend is `index.html` and calls the serverless function at `/api/send_email`.
- Ensure your SMTP credentials work from Vercel (some providers block outbound SMTP). Consider using an email provider API (SendGrid, Mailgun) if SMTP is blocked.
- The repository's CLI was moved to `cli_main.py` to avoid Vercel attempting to treat the CLI as a serverless function.
