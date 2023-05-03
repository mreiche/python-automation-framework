FROM debian:bookworm-slim

# https://askubuntu.com/questions/1095266/apt-get-update-failed-because-certificate-verification-failed-because-handshake
RUN apt -y update \
    && apt -y install wget chromium chromium-driver default-jre-headless \
    && apt clean

COPY selenium-server.jar .
RUN java -jar selenium-server.jar standalone --version \
    && whereis chromium \
    && chromedriver --version \
    && python3 --version

#RUN wget -d https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
#    && mv selenium-server-4.9.0.jar selenium-server.jar
