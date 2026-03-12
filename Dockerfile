FROM python:3.12-slim

# 1) 系统依赖：tesseract + 日语语言包 + 字体
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-jpn \
    fonts-noto-cjk \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) 代码
COPY app ./app

# 4) 启动
ENV PORT=10000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]