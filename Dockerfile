FROM python:3.15-slim

WORKDIR /app

# The Node driver bundled with Playwright needs libatomic, which the slim base lacks,
# and it must be present before `playwright install --with-deps` can run.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Bogota \
    RUNNING_IN_DOCKER=1

COPY conftest.py pytest.ini ./
COPY tests ./tests

ENTRYPOINT ["python", "-m", "pytest"]
CMD ["--markers"]
