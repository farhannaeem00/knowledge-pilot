"""
Prompt construction for summarization. One flexible template + a style
instruction map, rather than seven separate hardcoded prompts - keeps
the seven styles (executive, beginner, technical, bullet_points,
detailed, academic, content_creator) consistent and easy to extend.
"""
VALID_STYLES = {
    "executive",
    "beginner",
    "technical",
    "bullet_points",
    "detailed",
    "academic",
    "content_creator",
}

STYLE_INSTRUCTIONS = {
    "executive": "Write for a busy executive: concise, decision-oriented, focus on business impact.",
    "beginner": "Write for someone with no background in the topic: simple language, avoid jargon, explain concepts from scratch.",
    "technical": "Write for a technical/expert audience: precise terminology, assume domain familiarity.",
    "bullet_points": "Favor short bullet points over prose wherever possible, even within fields that are normally prose.",
    "detailed": "Write a thorough, comprehensive summary that doesn't skip nuance.",
    "academic": "Write in a formal academic register, citing structure/methodology where relevant.",
    "content_creator": "Write with an engaging, hook-driven tone suitable for turning into social/video content later.",
}

JSON_SCHEMA_INSTRUCTIONS = """
Respond with ONLY a single JSON object (no markdown fences, no commentary) with exactly these keys:

{
  "overview": string,
  "executive_summary": string,
  "key_ideas": [string, ...],
  "section_summary": [{"title": string, "summary": string}, ...],
  "important_concepts": [string, ...],
  "important_statistics": [string, ...],
  "examples": [string, ...],
  "pros": [string, ...],
  "cons": [string, ...],
  "actionable_insights": [string, ...],
  "key_takeaways": [string, ...],
  "conclusion": string,
  "reading_time_minutes": integer,
  "difficulty_level": one of "beginner" | "intermediate" | "advanced",
  "confidence_score": number between 0.0 and 1.0 representing how confident you are that this summary faithfully represents the source content
}

If a field genuinely doesn't apply to this content (e.g. no clear "cons"), use an empty array or empty string rather than omitting the key.
"""


def build_system_prompt(style: str) -> str:
    style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["detailed"])
    return (
        "You are an expert content summarizer for a knowledge management platform. "
        f"{style_instruction}\n\n{JSON_SCHEMA_INSTRUCTIONS}"
    )


def build_user_prompt(*, title: str, content: str) -> str:
    return f"Document title: {title}\n\nDocument content:\n{content}"
