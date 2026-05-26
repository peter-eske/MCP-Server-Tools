FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY advanced_debate_server.py .
COPY model_roles.yaml .

EXPOSE 8000

ENV PORT=8000

CMD ["python", "advanced_debate_server.py"]
