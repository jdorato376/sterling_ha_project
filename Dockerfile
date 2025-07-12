FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-configure git for safe operations
RUN git config --global --add safe.directory /app \
    && git config --global user.email "sterling@localhost" \
    && git config --global user.name "Sterling Bot"

# Copy dependency files first
COPY requirements.txt entrypoint.sh generate_env.sh ./

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set script permissions
RUN chmod +x entrypoint.sh generate_env.sh

# Copy the rest of the project (including optional .env)
COPY . .

# Ensure .env is secured if present
RUN if [ -f .env ]; then chmod 600 .env; fi

HEALTHCHECK --interval=60s --timeout=5s CMD curl -f http://localhost:5000/sterling/status || exit 1

ENTRYPOINT ["./entrypoint.sh"]

