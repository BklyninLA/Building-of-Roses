from transformers import pipeline

# Initialize once
summarizer = pipeline(
    "summarization",
    model="google/flan-t5-base",
    device=-1  # set to 0 if you have a GPU in your environment
)

def ai_summary(text: str) -> str:
    chunk = text[:1000]  # truncate long docs
    out   = summarizer(chunk, max_length=120, min_length=40, do_sample=False)
    return out[0]["summary_text"]
