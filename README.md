# PM Job App Prep

A CLI tool that takes a job description and generates tailored application materials — resume bullets, cover letter, and interview prep — in one shot.

## What it outputs

Given a JD, it produces:

1. **Keyword alignment** — the 5-8 most important terms from the JD mapped to your specific experiences
2. **Tailored resume bullets** — 5-7 of your strongest bullets rewritten to match the JD's language and priorities (real experiences, real metrics — nothing invented)
3. **Cover letter** — 3 paragraphs, no generic openers, no cliches. Why this company, one relevant story, what you'd do in 90 days.
4. **Role-specific interview prep** — 8-10 likely questions for this specific role, each with a 2-3 sentence angle on which story to use and why it fits

## Setup

```bash
pip install -r requirements.txt
cp profile.example.txt profile.txt   # copy the template
# edit profile.txt with your background — this file is gitignored
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

Interactive (paste JD when prompted):
```bash
python prep.py
```

From files:
```bash
python prep.py --jd jd.txt
python prep.py --jd jd.txt --notes extra_notes.txt
```

## Tips

- Your background lives in `profile.txt` (gitignored — never committed to GitHub)
- Use `--notes` to add role-specific context: experiences you want to highlight, research you've done on the company
- Save the output before closing — it streams directly to terminal

## Model

Uses Claude Opus 4.6 via the Anthropic API.

