FROM ubuntu:22.04

WORKDIR /home

RUN apt -y update \
    && apt -y install unzip curl default-jre-headless python3 python3-pip python3-venv \
    && curl -fLo chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt -y install ./chrome.deb \
    && rm chrome.deb \
    && ln -s /opt/google/chrome/chrome /usr/local/bin \
    && apt clean

RUN curl -fLo LATEST_RELEASE_STABLE https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE \
    && curl -fLo chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/`cat LATEST_RELEASE_STABLE`/linux64/chromedriver-linux64.zip \
    && unzip "chromedriver.zip" \
    && ln -s "/home/chromedriver-linux64/chromedriver" /usr/local/bin \
    && rm "chromedriver.zip" \
    && rm LATEST_RELEASE_STABLE

RUN python3 -m venv venv \
    && curl -fLo selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
    && java -jar selenium-server.jar standalone --version \
    && chrome --version \
    && chromedriver --version \
    && python3 --version \
    && pip --version
