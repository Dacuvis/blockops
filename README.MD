# blockops

A simple Minecraft Java Server Manager built with Python.

## Features

- Start Minecraft server using JAR.
- Custom RAM allocation.
- Real-time RAM monitoring.
- HTTP connectivity checker.

## Requirements

- Python 3.10+
- Java
- Minecraft Server JAR

## Installation

```bash
git clone https://github.com/Dacuvis/blockops.git
cd blockops
pip install typer psutil requests
```

## Usage

Start server:

```bash
python main.py connectserver --jar server.jar --ram 2G
```

Check connection:

```bash
python main.py respon --url https://google.com
```

## Built With

- Python
- Typer
- Psutil
- Requests
