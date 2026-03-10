import os
import json
import random
import requests
import datetime
from openai import OpenAI

# ── Clients ──────────────────────────────────────────────────────────────────
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

LINKEDIN_ACCESS_TOKEN  = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ORGANIZATION_ID = os.environ["LINKEDIN_ORGANIZATION_ID"]   # numeric ID only, e.g. 12345678

# ── Content system ────────────────────────────────────────────────────────────
# 7-day rotating pillars — index 0 = Monday … 6 = Sunday
PILLARS = [
    {
        "day":   "Monday",
        "theme": "Educational AI Content",
        "brief": (
            "Teach business owners something genuinely useful about AI agents. "
            "Break down a concept simply. Use an analogy. Make it feel accessible, "
            "not intimidating. No fluff — real insight they can act on."
        ),
    },
    {
        "day":   "Tuesday",
        "theme": "ROI & Cost Saving Math",
        "brief": (
            "Show the hard numbers. Pick a real business role or task and do the math "
            "on what a human costs vs what an AI agent costs. Be specific with dollar "
            "amounts and time savings. Make the ROI undeniable."
        ),
    },
    {
        "day":   "Wednesday",
        "theme": "Bullchain Labs Story / Behind the Scenes",
        "brief": (
            "Share something authentic about building Bullchain Labs and the AI consulting "
            "arm. A lesson learned, a challenge overcome, a build in progress. "
            "Founder-led content. Real and human."
        ),
    },
    {
        "day":   "Thursday",
        "theme": "Client Problem Spotlight",
        "brief": (
            "Describe a common problem that small or mid-sized businesses face — "
            "something repetitive, costly, or time-consuming — and explain exactly "
            "how an AI agent solves it. Be specific and practical."
        ),
    },
    {
        "day":   "Friday",
        "theme": "Engagement Question",
        "brief": (
            "Ask a punchy, thought-provoking question that business owners will want "
            "to answer in the comments. About AI, automation, business operations, "
            "or the future of work. Keep it short and scroll-stopping."
        ),
    },
    {
        "day":   "Saturday",
        "theme": "Industry News or Trend Take",
        "brief": (
            "Share a take on a current trend in AI, automation, or business technology. "
            "Be opinionated. Business owners respect a clear point of view. "
            "Don't sit on the fence."
        ),
    },
    {
        "day":   "Sunday",
        "theme": "Mindset / Motivation for Business Owners",
        "brief": (
            "Write something motivational but grounded — not cringe. Speak to the "
            "business owner who is grinding, building, and trying to stay ahead. "
            "Tie it back to the opportunity that AI and automation represents right now."
        ),
    },
]

# Previous topics log to avoid repetition (stored in a simple local file)
LOG_FILE = "posted_topics.json"

def load_recent_topics():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_topic(topic: str):
    topics = load_recent_topics()
    topics.append(topic)
    # Keep only last 30
    topics = topics[-30:]
    with open(LOG_FILE, "w") as f:
        json.dump(topics, f)

# ── Post generation ───────────────────────────────────────────────────────────
def generate_post(pillar: dict, recent_topics: list) -> str:
    recent_str = "\n".join(f"- {t}" for t in recent_topics[-10:]) if recent_topics else "None yet"

    system_prompt = """You are the voice of Bullchain Labs — an AI automation and business 
consulting company. Your tone is confident, direct, knowledgeable, and real. 
You speak to small and mid-sized business owners who are smart but busy. 
You never use corporate jargon or AI hype. You make complex things simple. 
You always lead with value. You are building authority and trust with every post.

LinkedIn post rules:
- Start with a scroll-stopping first line (no "Excited to share" or cringe openers)
- No hashtags at all
- No emojis
- Write in short punchy paragraphs — max 2-3 sentences each
- Total length: 150-250 words
- End with either a question, a call to action, or a powerful closing statement
- Sound like a real founder, not a marketing bot
- Never start with "I" as the first word"""

    user_prompt = f"""Write a LinkedIn post for today ({pillar['day']}).

Theme: {pillar['theme']}
Brief: {pillar['brief']}

Recent topics to AVOID repeating:
{recent_str}

Write the post now. Return only the post text, nothing else."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.85,
        max_tokens=400,
    )

    return response.choices[0].message.content.strip()

# ── LinkedIn posting ──────────────────────────────────────────────────────────
def get_linkedin_person_id() -> str:
    """Auto-fetch the numeric personal LinkedIn ID using the access token."""
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
    response.raise_for_status()
    data = response.json()
    # sub field contains the person ID
    person_id = data.get("sub", "")
    print(f"✅ LinkedIn Person ID: {person_id}")
    return person_id

def post_to_linkedin(text: str) -> dict:
    person_id = get_linkedin_person_id()
    url = "https://api.linkedin.com/v2/ugcPosts"

    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type":  "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    payload = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    today      = datetime.datetime.utcnow()
    weekday    = today.weekday()          # 0=Monday … 6=Sunday
    pillar     = PILLARS[weekday]

    print(f"[{today.strftime('%Y-%m-%d %H:%M UTC')}] Running agent — Theme: {pillar['theme']}")

    recent_topics = load_recent_topics()
    post_text     = generate_post(pillar, recent_topics)

    print("\n── Generated Post ──────────────────────────────────")
    print(post_text)
    print("────────────────────────────────────────────────────\n")

    result = post_to_linkedin(post_text)
    print(f"✅ Posted successfully! Post ID: {result.get('id', 'unknown')}")

    # Log the theme + first line to avoid repetition
    first_line = post_text.split("\n")[0][:80]
    save_topic(f"{pillar['theme']}: {first_line}")

if __name__ == "__main__":
    main()
