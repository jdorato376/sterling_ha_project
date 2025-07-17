# Stage 1: Build stage
FROM python:3.12-slim AS builder
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pull in all source (including run.sh/entrypoint.sh)
COPY . .
RUN chmod +x run.sh entrypoint.sh

# Stage 2: Runtime stage
FROM python:3.12-slim
WORKDIR /app

# Copy over the built app and dependencies
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Final entrypoint
ENTRYPOINT ["./run.sh"]
