FROM ubuntu:22.04

WORKDIR /home

RUN apt -y update \
    && apt -y install unzip wget default-jre-headless \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt -y install ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && ln -s /opt/google/chrome/chrome /usr/local/bin \
    && apt clean

RUN wget -O selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
    && wget https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE \
    && wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/`cat LATEST_RELEASE_STABLE`/linux64/chromedriver-linux64.zip \
    && unzip "chromedriver-linux64.zip" \
    && mv "chromedriver-linux64/chromedriver" /usr/local/bin \
    && rm "chromedriver-linux64.zip" \
    && rm LATEST_RELEASE_STABLE

RUN java -jar selenium-server.jar standalone --version \
    && chrome --version \
    && chromedriver --version \
    && python3 --version
