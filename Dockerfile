FROM python:3.11-slim

ARG SERVER_PORT=80
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN python -m pip install .

EXPOSE ${SERVER_PORT}
ENTRYPOINT ["streamlit", "run", "/app/cobp/__main__.py", "--server.port=${SERVER_PORT}", "--server.address=0.0.0.0"]