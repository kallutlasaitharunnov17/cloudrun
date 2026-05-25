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

## GitHub

Remote: `https://github.com/kallutlasaitharunnov17/cloudrun.git`
