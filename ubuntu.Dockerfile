FROM ubuntu:latest

WORKDIR /home

RUN apt -y update \
    && apt -y install unzip wget default-jre-headless \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt -y install ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && ln -s /opt/google/chrome/chrome /usr/local/bin \
    && apt clean

RUN wget -O selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
    && wget https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin \
    && rm chromedriver_linux64.zip

RUN java -jar selenium-server.jar standalone --version \
    && chrome --version \
    && chromedriver --version \
    && python3 --version
