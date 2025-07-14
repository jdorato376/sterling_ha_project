FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Copy files first (so chmod works)
COPY requirements.txt .
COPY entrypoint.sh .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Fix script permissions
RUN chmod +x entrypoint.sh

# Copy everything else
COPY . .

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

