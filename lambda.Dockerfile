FROM python:3.8.5

RUN apt update
RUN apt install -y mecab libmecab-dev mecab-ipadic-utf8 swig
RUN git clone --depth=1 https://github.com/neologd/mecab-ipadic-neologd
RUN cd ./mecab-ipadic-neologd && ./bin/install-mecab-ipadic-neologd -y -p /var/lib/mecab/dic/mecab-ipadic-neologd
RUN rm -rf ./mecab-ipadic-neologd
RUN ln -s /var/lib/mecab/dic /usr/lib/mecab/dic
RUN pip install awslambdaric
RUN mkdir /var/app
WORKDIR /var/app
COPY src/Pipfile ./
COPY src/Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --system
RUN cp /etc/mecabrc /usr/local/etc/mecabrc
COPY src/ ./
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.handler" ]