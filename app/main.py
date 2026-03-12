from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .pdf_text import extract_text_from_pdf
from .ocr import ocr_pdf
from .nlp import analyze_text
from .wordcloud_gen import generate_wordcloud
from .excel_export import generate_excel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_MB = 20
MIN_TEXT_LEN_BEFORE_OCR = 80


def parse_pdf_and_analyze(pdf_bytes: bytes):
    # 先尝试直接提取文本
    txt = extract_text_from_pdf(pdf_bytes)
    mode_used = "text"

    # 如果文本太少，说明可能是扫描版 PDF，走 OCR
    if len(txt.strip()) < MIN_TEXT_LEN_BEFORE_OCR:
        txt = ocr_pdf(pdf_bytes)
        mode_used = "ocr"

    result = analyze_text(txt)
    freq = result["all"]

    if not freq:
        raise HTTPException(
            status_code=422,
            detail="No tokens found. OCR may have failed or PDF is empty."
        )

    # 总表格前20
    top20 = [{"token": w, "count": c} for w, c in freq.most_common(20)]

    # 各词性前10
    noun_top10 = [{"token": w, "count": c} for w, c in result["名詞"].most_common(10)]
    verb_top10 = [{"token": w, "count": c} for w, c in result["動詞"].most_common(10)]
    adj_top10 = [{"token": w, "count": c} for w, c in result["形容詞"].most_common(10)]
    adv_top10 = [{"token": w, "count": c} for w, c in result["副詞"].most_common(10)]

    # 词云只显示总词频前10
    top10_freq = dict(freq.most_common(10))
    wc_b64 = generate_wordcloud(top10_freq)

    return {
        "mode_used": mode_used,
        "freq": freq,
        "top20": top20,
        "noun_top10": noun_top10,
        "verb_top10": verb_top10,
        "adj_top10": adj_top10,
        "adv_top10": adv_top10,
        "wordcloud_png_base64": wc_b64,
    }


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF too large (>{MAX_MB}MB).")

    result = parse_pdf_and_analyze(pdf_bytes)

    return {
        "mode_used": result["mode_used"],
        "total_tokens": sum(result["freq"].values()),
        "unique_tokens": len(result["freq"]),
        "top20": result["top20"],
        "noun_top10": result["noun_top10"],
        "verb_top10": result["verb_top10"],
        "adj_top10": result["adj_top10"],
        "adv_top10": result["adv_top10"],
        "wordcloud_png_base64": result["wordcloud_png_base64"],
    }


@app.post("/export_excel")
async def export_excel(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF too large (>{MAX_MB}MB).")

    result = parse_pdf_and_analyze(pdf_bytes)

    excel_file = generate_excel(
        top20=result["top20"],
        noun_top10=result["noun_top10"],
        verb_top10=result["verb_top10"],
        adj_top10=result["adj_top10"],
        adv_top10=result["adv_top10"],
    )

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=word_frequency_result.xlsx"
        }
    )