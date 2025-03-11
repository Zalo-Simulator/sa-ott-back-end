# Sử dụng Python base image
FROM python:3.10

# Đặt thư mục làm việc
WORKDIR /app

# Copy file requirements.txt và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Đảm bảo Alembic được cài đặt
RUN pip install alembic

# Copy toàn bộ mã nguồn vào container
COPY . .

# Chạy ứng dụng dưới quyền root
USER root

# Lệnh mặc định chạy FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
