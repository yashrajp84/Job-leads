from __future__ import annotations

INVITE_TMPL = (
    """
Return ONLY JSON: {"draft": "..."}.
Write a ~300 character LinkedIn invite.
Inputs:
- Name: {full_name}
- Company: {company}
- Headline: {headline}
- My context: {shared}
- Style: {style}
Keep it concise: 1 hook + 1 value + soft CTA.
"""
).strip()

COMMENT_TMPL = (
    """
Return ONLY JSON: {"draft": "..."}.
Write a 1–2 sentence comment adding insight (no praise-only).
Inputs:
- Post excerpt: {excerpt}
- Persona: {persona}
- Style: {style}
"""
).strip()

COVER_LETTER_TMPL = (
    """
Return ONLY JSON: {"draft": "..."}.
Write a short tailored cover letter paragraph + 4–6 resume bullets (quantified where possible).
Inputs:
- Job: {title} @ {company}
- Description: {description}
- My strengths: {strengths}
- Keywords: {keywords}
- Style: {style}
Keep it concise and copy-ready.
"""
).strip()

RESUME_BULLETS_TMPL = (
    """
Return ONLY JSON: {"draft": "..."}.
Write 4–6 resume bullets tailored to {title} @ {company}.
Use impact-first, quantified bullets aligned to: {keywords}
"""
).strip()

