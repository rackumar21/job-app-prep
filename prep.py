#!/usr/bin/env python3
"""
PM Job App Prep — CLI tool for tailoring your application to a specific job description.

Given a JD and your background (from profile.txt), outputs:
  1. Tailored resume bullets aligned to the role
  2. A cover letter (concise, story-driven)
  3. Role-specific interview questions + strong answer angles

Setup:
  cp profile.example.txt profile.txt   # copy the template
  edit profile.txt                      # fill in your background
  export ANTHROPIC_API_KEY=your_key_here

Usage:
  python prep.py                              # interactive prompts
  python prep.py --jd jd.txt                 # from file
  python prep.py --jd jd.txt --notes me.txt  # with extra context
"""

import os
import sys
import argparse
import anthropic

# ─────────────────────────────────────────────
# Load candidate profile
# ─────────────────────────────────────────────

def load_profile() -> str:
    profile_path = os.path.join(os.path.dirname(__file__), "profile.txt")
    if not os.path.exists(profile_path):
        print("\nError: profile.txt not found.")
        print("Copy the template and fill it in:")
        print("  cp profile.example.txt profile.txt\n")
        sys.exit(1)
    with open(profile_path) as f:
        return f.read().strip()


# ─────────────────────────────────────────────
# System prompt
# ─────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """You are a PM career coach helping a candidate tailor their application to a specific job.

Here is the candidate's background:
{profile}

## Your output for each job application:

### PART 1: KEYWORD ALIGNMENT
List the 5-8 most important keywords/phrases from the JD. For each, note which of the candidate's experiences maps to it best.

### PART 2: TAILORED RESUME BULLETS
Rewrite 5-7 of the candidate's strongest bullets to match the JD's language and priorities.
Format: [Role] - [bullet in "verb + context + metric/outcome" format]
Only use real experiences and real metrics from the profile. Do not invent.

### PART 3: COVER LETTER
Write a 3-paragraph cover letter. No generic openers.
- Para 1: Why this company specifically (1-2 concrete reasons tied to what they're building)
- Para 2: The one experience most relevant to this role, told as a story (not a list)
- Para 3: What the candidate would bring in the first 90 days
Tone: direct, warm, confident. No cliches ("I'm passionate about...", "I'm excited to...").

### PART 4: ROLE-SPECIFIC INTERVIEW PREP
List the 8-10 most likely interview questions for this specific role.
For each, give: the question + a 2-3 sentence "angle" (which story to use and why it fits).

Be specific. Generic PM advice is not useful here — tailor everything to the candidate's actual background and the specific role.
"""

# ─────────────────────────────────────────────
# Core function
# ─────────────────────────────────────────────

def run_prep(jd_text: str, notes: str | None = None):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nError: ANTHROPIC_API_KEY environment variable not set.")
        print("Export it: export ANTHROPIC_API_KEY=your_key_here\n")
        sys.exit(1)

    profile = load_profile()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(profile=profile)

    client = anthropic.Anthropic(api_key=api_key)

    user_content = f"JOB DESCRIPTION:\n{jd_text}"
    if notes:
        user_content += f"\n\nADDITIONAL NOTES:\n{notes}"

    print("\nGenerating your tailored application materials...\n")
    print("=" * 60)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system_prompt,
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
    parser.add_argument("--notes", help="Path to a .txt file with extra notes (optional)")
    args = parser.parse_args()

    jd_text = read_file_or_prompt(args.jd, "Paste the job description:")

    notes = None
    if not args.notes:
        add_notes = input("\nAdd any extra notes for this application? [y/N]: ").strip().lower()
        if add_notes == "y":
            notes = read_file_or_prompt(None, "Paste your notes:")
    else:
        notes = read_file_or_prompt(args.notes, "")

    run_prep(jd_text, notes)


if __name__ == "__main__":
    main()
