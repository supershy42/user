# srcs/user/Dockerfile

# Python 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./utils/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 애플리케이션 코드 복사
COPY ./config ./app

# Start ASGI server with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]