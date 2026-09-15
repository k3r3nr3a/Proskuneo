from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()


@register.filter
def youtube_embed(url):
    if not url:
        return ""

    url = str(url).strip()
    parsed = urlparse(url)

    # youtu.be/VIDEO_ID
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    # youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
    ):
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        # Ya es una URL /embed/
        if parsed.path.startswith("/embed/"):
            return url

    return url