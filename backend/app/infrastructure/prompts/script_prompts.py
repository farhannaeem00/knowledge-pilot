"""
Prompt construction for video/content script generation. One flexible
template + platform instruction map, same pattern as summary_prompts.py.
"""
VALID_PLATFORMS = {"youtube", "linkedin", "instagram_reel", "tiktok", "podcast", "presentation"}

PLATFORM_INSTRUCTIONS = {
    "youtube": "Write a YouTube video script. Assume a spoken, mid-length video (5-10 minutes). Include natural spoken transitions.",
    "linkedin": "Write a LinkedIn video/post script. Professional tone, hook must work in a scrolling feed, keep it tight (60-90 seconds spoken).",
    "instagram_reel": "Write an Instagram Reels script. Fast-paced, punchy, 30-60 seconds spoken, strong visual hook in the first 3 seconds.",
    "tiktok": "Write a TikTok script. Very fast-paced, conversational, hook in the first 2 seconds, 30-60 seconds spoken.",
    "podcast": "Write a podcast segment outline. Conversational, can be longer-form, include talking points rather than word-for-word script.",
    "presentation": "Write a presentation/slide-deck narration outline. Structure around slide-by-slide talking points.",
}

JSON_SCHEMA_INSTRUCTIONS = """
Respond with ONLY a single JSON object (no markdown fences, no commentary) with exactly these keys:

{
  "hook": string,
  "introduction": string,
  "body": [string, ...],
  "examples": [string, ...],
  "cta": string,
  "estimated_duration_seconds": integer
}

"body" should be an array of distinct talking-point/section strings, not one giant paragraph.
"""


def build_system_prompt(platform: str) -> str:
    instruction = PLATFORM_INSTRUCTIONS.get(platform, PLATFORM_INSTRUCTIONS["youtube"])
    return (
        "You are an expert content strategist turning source material into a script for a specific platform. "
        f"{instruction}\n\n{JSON_SCHEMA_INSTRUCTIONS}"
    )


def build_user_prompt(*, title: str, source_content: str) -> str:
    return f"Source title: {title}\n\nSource content:\n{source_content}"