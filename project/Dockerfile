FROM python:3.12

WORKDIR /usr/src/project/

COPY requirements requirements

RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt

COPY . .

ENTRYPOINT ["sh", "/usr/src/project/entrypoint.sh"]
# ENTRYPOINT ["tail", "-f"]
