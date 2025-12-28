# ./ollama/Dockerfile
FROM ollama/ollama:latest

RUN ollama pull defog/sqlcoder:7b-q4_0

ENTRYPOINT ["ollama", "serve"]
