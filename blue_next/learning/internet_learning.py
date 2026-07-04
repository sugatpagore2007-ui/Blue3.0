
import time, re, urllib.parse, requests
from html.parser import HTMLParser
from blue_next.memory.memory_store import MEMORY
from blue_next.memory.vector_memory import VECTOR_MEMORY
from blue_next.config.settings import SETTINGS

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]
    def handle_data(self, data):
        data=data.strip()
        if len(data)>40: self.text.append(data)

def trusted(url):
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
        return any(d in host for d in SETTINGS.trusted_domains)
    except Exception:
        return False

def summarize_text(text, max_chars=900):
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= max_chars: return clean
    # Simple free summarizer: first useful sentences. LLM summarization can be called later.
    sentences = re.split(r"(?<=[.!?])\s+", clean)
    out=[]
    for s in sentences:
        if len(" ".join(out)) + len(s) > max_chars: break
        out.append(s)
    return " ".join(out)[:max_chars]

def research_url(url, topic="internet research"):
    if not trusted(url):
        return f"Blocked untrusted source: {url}"
    try:
        html = requests.get(url, timeout=10, headers={"User-Agent":"BlueResearchBot/1.0"}).text
        parser = TextExtractor(); parser.feed(html)
        summary = summarize_text(" ".join(parser.text))
        kid = MEMORY.save_knowledge(topic, summary, url, trusted=1)
        VECTOR_MEMORY.add(summary, {"topic": topic, "source": url})
        return f"Learned trusted summary for {topic}. Memory id: {kid}"
    except Exception as e:
        return f"Internet learning failed: {e}"

def background_research(topic):
    # Free, safe starter: stores the search query as a pending research note.
    # Avoid blind scraping/searching unknown sites automatically.
    MEMORY.add_event("internet_learning_request", topic, "Pending approval/source URL needed")
    return ("Internet learning request saved. For safe learning, give me a trusted URL or approve sources first. "
            "Example: learn from internet https://docs.python.org/3/tutorial/ topic python")
