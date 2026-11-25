FROM python:3.15-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5

WORKDIR /app

# Browsers live outside any home directory so the container works with any
# uid (`docker run --user`), not just the one baked into the image.
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PYTHONDONTWRITEBYTECODE=1

# The Node driver bundled with Playwright needs libatomic, which the slim base lacks,
# and it must be present before `playwright install --with-deps` can run.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium \
    && chmod -R a+rX /ms-playwright \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=America/Bogota \
    RUNNING_IN_DOCKER=1

COPY conftest.py pytest.ini ./
COPY tests ./tests

# The run writes results, screenshots, failure captures and the pytest cache
# here; with bind mounts the host owns them, otherwise these folders must
# accept any uid.
RUN useradd --uid 1000 --create-home pwuser \
    && mkdir reports evidencias test-results .pytest_cache \
    && chmod 777 reports evidencias test-results .pytest_cache

USER 1000

ENTRYPOINT ["python", "-m", "pytest"]
CMD ["--markers"]
