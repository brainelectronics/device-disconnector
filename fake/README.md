# Fake device-disconnector

Device disconnector fake application for testing

---

<!-- MarkdownTOC -->

- [Setup](#setup)
    - [Local development](#local-development)
    - [Docker development](#docker-development)
        - [Docker Compose](#docker-compose)
        - [Just Docker](#just-docker)
        - [Run example calls](#run-example-calls)

<!-- /MarkdownTOC -->

## Setup

### Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
export FLASK_DEBUG=1
export FLASK_APP=project/main.py
flask run
```

### Docker development

Add `-d` to the command to execute in detached mode

#### Docker Compose

```bash
docker compose up -d --no-deps --build

# check running
docker ps

# stop running
docker compose down --remove-orphans
```

#### Just Docker

```bash
docker build --tag 'device-disconnector' .

# run a clean new instance named "device-disconnector"
docker run --rm -p 5099:5099 --name 'device-disconnector' 'device-disconnector'

# check running
docker ps

# stop container by name
docker stop 'device-disconnector'
```

#### Run example calls

```bash
cd ..
poetry run control-device \
    127.0.0.1:5000 \
    usb3=on \
    switch1=on \
    -vvvv
```
