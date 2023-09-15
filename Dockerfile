FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN python -m pip install .

EXPOSE 80
ENTRYPOINT ["streamlit", "run", "/app/cobp/__main__.py", "--server.port=80", "--server.address=0.0.0.0"]