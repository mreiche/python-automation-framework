FROM paf-test-base:latest

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY pytest.ini pytest.ini
COPY test test
COPY paf paf
