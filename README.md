# Weather Forecast API With Django

This is a Django demo project that showcases my coding styles and structure for a django project. Includes Docker support for easy setup and deployment.

## Prerequisites

- Python 3.11 (minimum)
- (Optinoal) Docker installed on your machine
- (Optional) Docker Compose installed on your machine

## Project Setup (Docker)

### 1. Clone the Repository

```sh
git clone git@github.com:jiaulislam/weather-forecast-technical-assignment.git
cd weather-forecast-technical-assignment
```

### 2. Run Project with Docker

```sh
docker build -t weather-app .
docker run --name weather-app-container -p 8080:8080 weather-app
```

### 3. Run Tests

```sh
docker exec -it weather-app-container pytest
```
> previously while running docker container specifically named the container with 'weather-app-container'

## Project Setup (virtualenv)

### 1. Clone the Repository

```sh
git clone git@github.com:jiaulislam/weather-forecast-technical-assignment.git
cd weather-forecast-technical-assignment
```

### 2. Install Poetry

```sh
pip install poetry
```

### 3. Install Dependencies

```sh
poetry install
```

### 4. Activate the VirtualEnv

```sh
poetry shell
```

### 5. Make migrations & Run Project with Poetry VirtualEnv

```sh
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:8080
```

## Run Tests

```sh
poetry run pytest
```

# Swagger UI

RestAPI documentation has been configured for this project. To see the documentation please
visit below URL.


> http://localhost:8080/

or

> http://localhost:8080/api/docs

# For Development Contribution
For development purpose before commiting on the project please install `pre-commit`. So our hooks on every commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements. By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change while not wasting time with trivial style nitpicks.

```sh
poetry add -G dev pre-commit
pre-commit install
pre-commit run -c ./pre-commit-config.yaml
```
