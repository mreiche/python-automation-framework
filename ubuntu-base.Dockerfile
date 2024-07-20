FROM ubuntu:22.04

WORKDIR /home

RUN CHROME_HEADLESS_DEPS="libglib2.0-0 libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libasound2"; \
    TOOLS="unzip curl"; \
    SELENIUM="default-jre-headless"; \
    PYTHON="python3 python3-venv"; \
    apt -y update \
    && apt -y install ${TOOLS} ${SELENIUM} ${PYTHON} ${CHROME_HEADLESS_DEPS} \
    && apt clean

RUN curl -fLo chrome-headless.zip https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.182/linux64/chrome-headless-shell-linux64.zip \
    && unzip chrome-headless.zip \
    && mv chrome-headless-shell-linux64 /opt \
    && ln -s /opt/chrome-headless-shell-linux64/chrome-headless-shell /usr/local/bin/chrome \
    && rm chrome-headless.zip \
    && curl -fLo LATEST_RELEASE_STABLE https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE \
    && curl -fLo chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/`cat LATEST_RELEASE_STABLE`/linux64/chromedriver-linux64.zip \
    && unzip "chromedriver.zip" \
    && ln -s "/home/chromedriver-linux64/chromedriver" /usr/local/bin \
    && rm "chromedriver.zip" \
    && rm LATEST_RELEASE_STABLE

# Copy everything according .Dockerignore
COPY . .

RUN apt -y update  \
    && apt -y install python3-pip \
    && python3 -m venv venv \
    && pip install -r requirements.txt \
    && apt -y purge python3-pip \
    && apt -y autopurge \
    && apt clean

RUN curl -fLo selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
    && java -jar selenium-server.jar standalone --version \
    && chromedriver --version \
    && python3 --version

# This doesn't work
# ./chrome-headless-shell --headless --no-sandbox --disable-gpu --disable-gpu-sandbox --dump-dom https://www.chromestatus.com/
# chrome --no-sandbox --disable-gpu-sandbox
