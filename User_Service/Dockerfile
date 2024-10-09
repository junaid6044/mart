FROM python:3.12

WORKDIR /user_service

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry 

COPY . /user_service/

RUN poetry config virtualenvs.create false

RUN poetry install

EXPOSE 8003

CMD ["poetry", "run", "uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
