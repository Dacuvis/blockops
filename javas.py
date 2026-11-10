import subprocess
from pathlib import Path

import typer


def java_checker():
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5, check=False)
        if result.returncode == 0:
            typer.secho("Java berhasil ditemukan", fg=typer.colors.BRIGHT_GREEN)
            typer.echo(result.stderr)
            return True

        typer.secho("Java tidak dapat dijalankan", fg=typer.colors.RED)
        return False
    
    except FileNotFoundError:
        typer.secho("Java belum terinstall", fg=typer.colors.RED)
        return False

def java_validate(jar: str):
    file = Path(jar).expanduser()

    if not file.exists():
        typer.secho("File tidak exist", fg=typer.colors.RED)
        return False

    if not file.is_file():
        typer.secho("Path bukan sebuah file", fg=typer.colors.RED)
        return False

    if file.suffix.lower() != ".jar":
        typer.secho("File harus berekstensi .jar", fg=typer.colors.RED)
        return False

    typer.secho("File jar valid", fg=typer.colors.BRIGHT_GREEN)
    return True

def server_console(process):
    while process.poll() is None:
        try:
            command = input("server>")

            if not command.strip():
                continue
                
            process.stdin.write(command + "\n")
            process.stdin.flush()

        except (BrokenPipeError, OSError, EOFError):
            break