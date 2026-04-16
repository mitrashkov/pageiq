# ================================
# Python Dependencies Stage
# ================================
FROM python:3.11-slim as python-deps

# Set working directory
WORKDIR /tmp

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ================================
# Playwright Browsers Stage
# ================================
FROM python:3.11-slim as playwright-install

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and browsers
RUN pip install playwright==1.40.0 && \
    playwright install chromium && \
    playwright install-deps

# ================================
# Production Stage
# ================================
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from deps stage
COPY --from=python-deps /root/.local/lib/python3.11/site-packages /root/.local/lib/python3.11/site-packages
COPY --from=python-deps /root/.local/bin /root/.local/bin
ENV PATH=/root/.local/bin:$PATH

# Copy Playwright browsers from playwright stage
COPY --from=playwright-install /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=playwright-install /root/.local/lib/python3.11/site-packages/playwright /root/.local/lib/python3.11/site-packages/playwright

# Copy application code
COPY . .

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]