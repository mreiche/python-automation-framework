FROM ubuntu:latest

RUN apt -y update \
    && apt install -y chromium-browser chromium-chromedriver wget default-jre-headless \
    && apt clean

COPY selenium-server.jar .
RUN java -jar selenium-server.jar standalone --version

#RUN wget -d https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
#    && mv selenium-server-4.9.0.jar selenium-server.jar
