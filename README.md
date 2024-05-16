# An API for interacting with the Graph

## Interact with the API 🤝

- Start the API 🏁:
```commandline
python -m graph_api
```
- View the API documentation 📚: http://0.0.0.0:8000/docs

List of available routes 📍: 
- GET request:  http://0.0.0.0:8000/graph/welcome

## Dockerization 🐳

Build a docker image that exposes the API:
```commandline
make docker-build
```

Create a container based on the docker image and open an interactive terminal
```commandline
make docker-run
```

The API can start either through Docker or through python, with the commands that have been declared

## Deployment 🚀
- Start a screen 
```commandline
screen -S session_name
```

- Start the API
```commandline
python -m graph_api
```
- Detach the screen
press control + A + D

View the screens (detached and no detached)
```commandline
screen -ls
```

Resume a detached screen session
```commandline
screen -r session_name
```

Terminate an attached session
```commandline
screen -X -S session_name quit
```

## Development 🐍

### Requirements: 
    - python 3.12
    - pipenv for dependency management

- Create a virtual environment
```commandline
 pipenv --python 3.12
```
- Activate the environment
```commandline
pipenv shell
```

- Install the dependencies from Pipfile
```commandline
pipenv install --dev
```

If the error 
```ModuleNotFoundError: No module named 'distutils'``` appears then execute:
```commandline
pip install setuptools
```

### Check styling and formatting 🖋️
Check basic styling issues using flake8 linter
```commandline
make lint
```

Correctly format the order of the dependencies' imports 
```commandline
make isort
```

Forma the code using black
```commandline
make black
```

Check typing errors
```commandline
make mypy
```

### Contributing 🧩

CONTRIBUTING.md contains instructions about the branching model and the 
format of the commit messages.

CHANGELOG.md contains the changes that are included in each new version.

### Logging 🪵

Log messages are reported both in the console and in log files. A log file is
generated every time the app starts and stored in a log file named with the current
date-time information, within a logs file
