FROM python:3

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/

#ENTRYPOINT ["/bin/bash"]
