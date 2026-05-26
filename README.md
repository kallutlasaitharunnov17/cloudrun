# Cloudrun Rectangle App

This repository contains two Flask applications:

- `logic/` — login service intended to run on port `5000`
- `rectangle_app/` — rectangle calculator app intended to run on port `5001`

## Features

- `rectangle_app` lets a user enter length and breadth
- users choose whether to calculate `area` or `perimeter`
- results display on a styled result page
- `logic` provides the login page and authentication flow

## Run locally

```bash
cd logic
python app.py
```

```bash
cd rectangle_app
python app.py
```

## Deployment

Deploy `logic` on port `5000` and `rectangle_app` on port `5001` on your host or server.

## Architecture

- `logic/` is the login service on port `5000`
- `rectangle_app/` is the calculator UI and business logic on port `5001`
- `/logout` in the calculator app redirects users back to the login app on port `5000`

Example architecture:

```
USER (Browser)
    |
    v
INTERNET / PUBLIC IP
    |
    +----------------------+  +----------------------+
    | LOGIN UI APP (EC2)   |  | RECTANGLE API APP    |
    | Amazon EC2 Instance  |  | Amazon EC2 Instance  |
    | Port: 5000           |  | Port: 5001           |
    | - /login             |  | - /home              |
    | - /logout -> 5000    |  | - /calculate         |
    +----------------------+  +----------------------+
```

## GitHub

Remote: `https://github.com/kallutlasaitharunnov17/cloudrun.git`
