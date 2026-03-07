# Bullchain Labs LinkedIn Agent

Automatically generates and posts a fresh LinkedIn post every morning at 9AM PST to the Bullchain Labs company page. Powered by GPT-4o and the LinkedIn API.

## How It Works

- Runs daily at 9AM PST via Render Cron Job
- Rotates through 7 content pillars (one per day of the week)
- Uses GPT-4o to write a unique, on-brand post each day
- Remembers the last 30 topics to avoid repetition
- Posts directly to your LinkedIn company page

## Content Pillars

| Day | Theme |
|-----|-------|
| Monday | Educational AI Content |
| Tuesday | ROI & Cost Saving Math |
| Wednesday | Bullchain Labs Story / Behind the Scenes |
| Thursday | Client Problem Spotlight |
| Friday | Engagement Question |
| Saturday | Industry News or Trend Take |
| Sunday | Mindset / Motivation |

## Setup

### 1. Environment Variables (set these in Render)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `LINKEDIN_ACCESS_TOKEN` | Your LinkedIn OAuth access token |
| `LINKEDIN_ORGANIZATION_ID` | Your LinkedIn company numeric ID (numbers only) |

### 2. Finding Your LinkedIn Organization ID

1. Go to your Bullchain Labs LinkedIn company page
2. Click "Admin tools" → "Edit page"
3. Look at the URL — it will contain a number like `/company/12345678/`
4. That number is your Organization ID

### 3. Deploy on Render

1. Push this repo to GitHub
2. Go to render.com → New → Blueprint
3. Connect your GitHub repo
4. Render will detect render.yaml automatically
5. Add your environment variables in the Render dashboard
6. Deploy

## Token Renewal

LinkedIn access tokens expire every **2 months**. Set a reminder to regenerate your token at:
linkedin.com/developers/tools/oauth/token-generator

Then update the `LINKEDIN_ACCESS_TOKEN` environment variable in Render.
