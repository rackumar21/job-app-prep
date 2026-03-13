#!/usr/bin/env python3
"""
PM Job App Prep — CLI tool for tailoring your application to a specific job description.

Given a JD and your resume/background, outputs:
  1. Tailored resume bullets aligned to the role
  2. A cover letter (concise, story-driven)
  3. Role-specific interview questions + strong answer angles

Usage:
  python prep.py                              # interactive prompts
  python prep.py --jd jd.txt --resume me.txt # from files
"""

import os
import sys
import argparse
import anthropic

# ─────────────────────────────────────────────
# System prompt
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are a PM career coach helping a candidate tailor their application to a specific job.

The candidate is Rachita Kumar:
- Senior PM at PayPal (Checkout team, June 2024-present, San Jose CA)
  - Shipped App Switch: PayPal's first mobile checkout, 0-to-1. +450 bps conversion, +$50M incremental TPV.
  - Designed Instant Vault (zero-friction account linking): +256 bps conversion, +526 bps vaulting success
  - Owned A/B conversion program (6+ concurrent tests/sprint): +300 bps from scaled winners
- Founding PM at TruthSeek (voice AI qualitative research, stealth, 2025-present)
  - Designed LLM voice interview agent; eval-to-prompt iteration loop improved follow-up quality 2.8->4.1/5 (+46%)
  - Improved call completion 38%->61% through funnel analysis + prompt rewrites
  - Built eval framework to measure AI interview quality; ran live CPG consumer research studies
- Built Lunar solo: AI women's health companion (React, Supabase, Claude API, Vercel)
  - Cycle tracking, symptom logging, lab report uploads, AI chat with persistent memory
  - Engineering decisions: Supabase over Firebase (SQL portability + RLS), Claude over GPT (cost + health data stance)
- Prior: Madison India Capital (PE), Premji Invest (public equity), Deutsche Bank (IB)
- MBA: Wharton 2022-24 (GMAT 750, 98th%ile, Joseph Wharton Fellow, STEM - Business Analytics + Entrepreneurship)
- Undergrad: SRCC Delhi University, Rank 6/705

Target company profile: AI-native B2B SaaS (Decagon, Sierra, Harvey, Listen Labs type). Agent-focused, Series B/C, 50-300 people. PMs expected to be forward-deployed, customer-facing, technical enough to go deep on LLM behavior.

## Your output for each job application:

### PART 1: KEYWORD ALIGNMENT
List the 5-8 most important keywords/phrases from the JD. For each, note which of Rachita's experiences maps to it best.

### PART 2: TAILORED RESUME BULLETS
Rewrite 5-7 of Rachita's strongest bullets to match the JD's language and priorities.
Format: [Role] - [bullet in "verb + context + metric/outcome" format]
Only use real experiences and real metrics. Do not invent.

### PART 3: COVER LETTER
Write a 3-paragraph cover letter. No generic openers.
- Para 1: Why this company specifically (1-2 concrete reasons tied to what they're building)
- Para 2: The one experience most relevant to this role, told as a story (not a list)
- Para 3: What you'd bring in the first 90 days
Tone: direct, warm, confident. No cliches ("I'm passionate about...", "I'm excited to...").

### PART 4: ROLE-SPECIFIC INTERVIEW PREP
List the 8-10 most likely interview questions for this specific role.
For each, give: the question + a 2-3 sentence "angle" (which story to use and why it fits).

Be specific. The candidate will be interviewing at an AI startup — generic PM advice is not useful here.
"""

# ─────────────────────────────────────────────
# Core function
# ─────────────────────────────────────────────

def run_prep(jd_text: str, resume_notes: str | None = None):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nError: ANTHROPIC_API_KEY environment variable not set.")
        print("Export it: export ANTHROPIC_API_KEY=your_key_here\n")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    user_content = f"JOB DESCRIPTION:\n{jd_text}"
    if resume_notes:
        user_content += f"\n\nADDITIONAL CONTEXT / RESUME NOTES:\n{resume_notes}"

    print("\nGenerating your tailored application materials...\n")
    print("=" * 60)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n" + "=" * 60)
    print("\nDone. Save this output before closing.")


def read_file_or_prompt(filepath: str | None, prompt_text: str) -> str:
    if filepath:
        if not os.path.exists(filepath):
            print(f"Error: file not found: {filepath}")
            sys.exit(1)
        with open(filepath) as f:
            return f.read()

    print(f"\n{prompt_text}")
    print("(Paste below, then press Enter twice when done)\n")
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
            if len(lines) >= 2 and lines[-1] == "" and lines[-2] == "":
                break
        except EOFError:
            break
    return "\n".join(lines).strip()


# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PM Job App Prep — tailored bullets, cover letter, and interview prep for a specific JD."
    )
    parser.add_argument("--jd", help="Path to a .txt file containing the job description")
    parser.add_argument(
        "--resume",
        help="Path to a .txt file with additional resume context or notes (optional)",
    )
    args = parser.parse_args()

    jd_text = read_file_or_prompt(args.jd, "Paste the job description:")
    resume_notes = None
    if not args.resume:
        add_notes = input("\nAdd any extra context or custom notes? [y/N]: ").strip().lower()
        if add_notes == "y":
            resume_notes = read_file_or_prompt(
                None, "Paste your additional notes (specific experiences to highlight, etc.):"
            )
    else:
        resume_notes = read_file_or_prompt(args.resume, "")

    run_prep(jd_text, resume_notes)


if __name__ == "__main__":
    main()
