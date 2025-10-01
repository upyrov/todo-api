# TODO API

Task management API implemented as a test task for [Automaze](https://automaze.io).

## Getting started

Clone the repository:

```
git clone https://github.com/upyrov/todo-api.git
cd todo-api
```

Copy the example environment file and adjust it as needed:

`cp .env.example .env`

Activate the environment:

`source .venv/bin/activate`

Run the application:

`uv run uvicorn project.app:app --reload --env-file .env`

## Documentation

Access OpenAPI Specification at:

`http://127.0.0.1:8000/docs`

## License

TODO API is distributed under the terms of [GNU General Public License v3.0](./LICENSE).
