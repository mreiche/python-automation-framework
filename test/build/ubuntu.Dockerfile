FROM ubuntu:latest

# https://askubuntu.com/questions/1095266/apt-get-update-failed-because-certificate-verification-failed-because-handshake
RUN printf "Acquire { https::Verify-Peer false }\n" > /etc/apt/apt.conf.d/peers.conf \
    && apt -y update\
    && apt -y install software-properties-common \
    && add-apt-repository ppa:savoury1/chromium \
    && apt -y update \
    && apt -y install chromium-browser chromium-chromedriver wget default-jre-headless \
    && apt clean

COPY selenium-server.jar .
RUN java -jar selenium-server.jar standalone --version \
    && whereis chromium \
    && chromium --version \
    && chromedriver --version \
    && python --version

#RUN wget -d https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar \
#    && mv selenium-server-4.9.0.jar selenium-server.jar
