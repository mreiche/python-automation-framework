FROM debian:bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt -y update \
    && apt -y install wget chromium-shell chromium-driver default-jre-headless python3-pip python3-venv \
    && apt clean

WORKDIR /home
RUN wget -O selenium-server.jar https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar
RUN ln -s /usr/bin/python3 /usr/bin/python \
    && rm /usr/bin/chromium \
    && ln -s /usr/bin/chromium-shell /usr/bin/chromium \
    && java -jar selenium-server.jar standalone --version \
    #&& chromium --headless --no-sandbox --version \
    && chromedriver --version \
    && python --version
