import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from support_bot.knowledge_base import load_pdf, chunk_text, search_chunks, load_from_url

load_dotenv()
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ["GROQ_API_KEY"]

knowledge_base: list[str] = []
chat_history:   list[dict] = []
doc_loaded:     str = ""


class LoadRequest(BaseModel):
    pdf_path: str = ""
    pdf_url:  str = ""

class ChatRequest(BaseModel):
    message: str


@app.post("/load")
async def load_document(req: LoadRequest):
    global knowledge_base, chat_history, doc_loaded

    if req.pdf_url:
        try:
            logger.info(f"Loading from URL: {req.pdf_url[:80]}")
            text = load_from_url(req.pdf_url)
            source = req.pdf_url.split("/")[-1].split("?")[0] or "remote_doc"
        except Exception as e:
            logger.error(f"URL load failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    elif req.pdf_path:
        if not os.path.exists(req.pdf_path):
            raise HTTPException(status_code=404, detail=f"File not found: {req.pdf_path}")
        logger.info(f"Loading from path: {req.pdf_path}")
        text = load_pdf(req.pdf_path)
        source = req.pdf_path

    else:
        raise HTTPException(status_code=400, detail="Provide pdf_path or pdf_url")

    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text. PDF may be scanned.")

    knowledge_base = chunk_text(text)
    chat_history   = []
    doc_loaded     = source

    logger.info(f"Loaded: {source} → {len(knowledge_base)} chunks")
    return {
        "status": "loaded",
        "source": source,
        "chunks": len(knowledge_base),
        "chars":  len(text)
    }


@app.post("/ask")
async def chat(req: ChatRequest):
    global chat_history
    logger.info(f"CHAT HIT: {req.message[:50]}")
    if not knowledge_base:
        return {"answer": "No document loaded yet. Please load a PDF first."}
    relevant_chunks = search_chunks(req.message, knowledge_base, top_k=3)
    context = "\n\n---\n\n".join(relevant_chunks)
    system_prompt = f"""You are a helpful customer support assistant.
Answer questions based ONLY on the document context provided below.
If the answer is not in the context, say: "I don't have that information in the document. Please contact our support team directly."
Never make up information not present in the context.
Keep answers concise — 2-4 sentences unless detail is needed.
When answering questions involving math or formulas, always use LaTeX notation: inline math with $...$ and display math with $$...$$. For example: $(ab)^{{-1}} = b^{{-1}}a^{{-1}}$.

Document context:
{context}"""
    messages = [{"role": "system", "content": system_prompt}]
    messages += chat_history[-8:]
    messages.append({"role": "user", "content": req.message})
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 300,
            }
        )
    answer = response.json()["choices"][0]["message"]["content"].strip()
    chat_history.append({"role": "user",      "content": req.message})
    chat_history.append({"role": "assistant", "content": answer})
    escalate = any(phrase in answer.lower() for phrase in [
        "don't have that information", "not in the document",
        "i'm not sure", "contact our support",
    ])
    return {"answer": answer, "escalate": escalate, "chunks_used": len(relevant_chunks)}


@app.delete("/reset")
async def reset():
    global knowledge_base, chat_history, doc_loaded
    knowledge_base = []
    chat_history   = []
    doc_loaded     = ""
    return {"status": "reset"}


@app.get("/status")
async def status():
    return {"doc_loaded": doc_loaded, "chunks": len(knowledge_base), "history_turns": len(chat_history) // 2}

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "running"}


app.mount("/", StaticFiles(directory="support_bot/static", html=True), name="static")