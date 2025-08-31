FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    vim \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
# Force CPU-only mode for PyTorch
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_CUDA_AVAILABLE="false"
ENV CUDA_DEVICE_ORDER="PCI_BUS_ID"
ENV PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "--timeout", "1200", "main:app"]