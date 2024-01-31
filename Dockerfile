FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN apt-get -y update && \
	apt-get -y install curl grep tar wget bzip2
	
RUN apt-get update -y \
    && apt-get install --no-install-recommends --no-install-suggests -y tzdata ca-certificates bzip2 curl wget libc-dev libxt6 \
    && apt-get install --no-install-recommends --no-install-suggests -y `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
    && update-ca-certificates \
    # Cleanup unnecessary stuff && apt-get purge -y --auto-remove \
                  -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* /tmp/*
	

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz && \
    tar -zxf geckodriver-v0.33.0-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-v0.33.0-linux64.tar.gz

RUN wget -O firefox-setup.tar.bz2 "https://download.mozilla.org/?product=firefox-112.0.1&os=linux64" && \
	tar xjf firefox-setup.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm firefox-setup.tar.bz2

COPY pyMergeTagger.py .

CMD [ "python3", "pyMergeTagger.py" ]
