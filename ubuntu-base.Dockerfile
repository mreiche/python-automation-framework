FROM ubuntu:22.04

WORKDIR /home

RUN CHROME_HEADLESS_DEPS="libglib2.0-0 libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libasound2"; \
    TOOLS="unzip curl"; \
    SELENIUM="default-jre-headless"; \
    PYTHON="python3 python3-venv"; \
    apt -y update \
    && apt -y install ${TOOLS} ${SELENIUM} ${PYTHON} ${CHROME_HEADLESS_DEPS} \
    && apt clean

ARG DOWNLOAD_ARCH="linux64"

RUN curl -fLo LATEST_RELEASE_STABLE https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE \
    && export RELEASE=$(cat LATEST_RELEASE_STABLE) \
    && echo "Using release: ${RELEASE} for arch: ${DOWNLOAD_ARCH}" \
    && curl -fLo chrome-headless.zip https://storage.googleapis.com/chrome-for-testing-public/${RELEASE}/${DOWNLOAD_ARCH}/chrome-headless-shell-${DOWNLOAD_ARCH}.zip \
    && unzip chrome-headless.zip \
    && mv chrome-headless-shell-${DOWNLOAD_ARCH} /opt \
    && ln -s /opt/chrome-headless-shell-${DOWNLOAD_ARCH}/chrome-headless-shell /usr/local/bin/chrome \
    && rm chrome-headless.zip \
    && curl -fLo chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${RELEASE}/${DOWNLOAD_ARCH}/chromedriver-${DOWNLOAD_ARCH}.zip \
    && unzip "chromedriver.zip" \
    && ln -s "/home/chromedriver-${DOWNLOAD_ARCH}/chromedriver" /usr/local/bin \
    && rm "chromedriver.zip" \
    && rm LATEST_RELEASE_STABLE

# Copy everything according .Dockerignore
COPY . .

RUN python3 -m venv venv \
    && source venv/bin/activate \
    && apt -y update \
    && apt -y install python3-pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt -y purge python3-pip \
    && apt -y autopurge \
    && apt clean

RUN curl -fLo selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
    && java -jar selenium-server.jar standalone --version \
    && chromedriver --version \
    && chrome --headless --no-sandbox --disable-gpu --disable-gpu-sandbox --dump-dom https://www.chromestatus.com/ \
    && python --version
