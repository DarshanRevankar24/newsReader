FROM python:3.9-slim

WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 user

# Install system dependencies if needed (e.g. for some pip packages)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY --chown=user:user . .

# Switch to the non-root user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Expose the Hugging Face Spaces port
EXPOSE 7860

# Command to run both safely out of shell '&' weirdness
CMD ["python", "run_both.py"]
