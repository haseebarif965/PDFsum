from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
import string
import heapq
from io import BytesIO

nltk.download("punkt")
nltk.download("stopwords")

app = FastAPI()  # ✅ THIS MUST BE PRESENT


# Allow frontend (like Vercel) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PDF Summarizer API is running 🚀"}

@app.post("/summarize/")
async def summarize(file: UploadFile = File(...), max_sentences: int = 5):
    content = await file.read()
    text = extract_text_from_pdf(content)
    summary = summarize_text(text, max_sentences)
    return {"summary": summary}

def extract_text_from_pdf(file_bytes):
    try:
        pdf_stream = BytesIO(file_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        return full_text
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

def summarize_text(text, max_sentences=5):
    if not text or len(text.strip()) < 100:
        return "⚠️ The document is too short or empty to summarize."

    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if word not in stop_words and word not in string.punctuation]

    word_frequencies = {}
    for word in words:
        word_frequencies[word] = word_frequencies.get(word, 0) + 1

    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies and len(sentence.split(" ")) < 30:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]

    summary_sentences = heapq.nlargest(max_sentences, sentence_scores, key=sentence_scores.get)
    summary = " ".join(summary_sentences)
    return summary
print ('hello')
