# Sử dụng Python 3.9 lightweight image
FROM python:3.9-slim-bullseye

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Định nghĩa thư mục làm việc
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies, set up virtual environment, install awscli
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-venv awscli && \
    python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt && \
    apt-get remove -y gcc && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


# Copy source code
COPY . .

# Tạo user không có quyền root để tăng bảo mật
RUN groupadd --gid 1000 app_group && \
    useradd --system --uid 1000 --gid app_group app_user && \
    chown -R app_user:app_group /app

# Chạy dưới user không phải root
USER app_user

# Mở port 8000
EXPOSE 8000

ENV SQL_DATABASE_URL="database-1.c10aqc840gk4.us-east-1.rds.amazonaws.com"

# Chạy ứng dụng
CMD ["/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
