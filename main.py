import subprocess
import threading
from collections import deque

import psutil
import requests as rq
import typer
from typer import Option

from btop import run_dashboard
from javas import java_checker, java_validate

app = typer.Typer()

@app.command()
def respon(url: str = Option(..., "--url", "-u", help="URL target yang ingin dicek")) -> str:
    res = rq.get(url)
    if res.status_code == 200:
        return print("Jaringan terkoneksi")
    else:
        return print("500, atau error lain")

@app.command()
def setup():
    cmd = ["wget", "https://api.papermc.io/v2/projects/paper/versions/26.3/builds/246/downloads/paper-26.3-246.jar", "-O", "server.jar"]

    try:
        typer.secho("Menyiapkan Server PaperMC", fg=typer.colors.GREEN)
        subprocess.run(cmd, check=True)

        typer.secho("Membuat file eula.txt")
        with open("eula.txt", "w") as f:
            f.write("eula=true\n")

        typer.secho("File dan Eula.txt sudah siap")

    except subprocess.CalledProcessError as e:
        typer.secho(f"Gagal mengunduh server jar lewat wget : {e}", err=True)
    except OSError as e:
        typer.secho(f"Terjadi kesalahan: {e}", err=True)
        
@app.command()
def connect_server(
    ram: str = Option("2G", "--ram", "-r", help="Masukan jumlah ram yang ingin dialokasi"),
    jar: str = Option(..., "--jar", "-j", help="Server jar"),
):

    if not java_checker():
        raise typer.Exit(code=1)

    if not java_validate(jar):
        raise typer.Exit(code=1)
    
    typer.echo("Menyiapkan server....")
    typer.echo(f"Alokasi ram: {ram}")
    typer.echo(f"file server: {jar}")

    cmd = ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", jar, "nogui"]

    console_logs = deque(maxlen=100)
    console_logs_lock = threading.Lock()

    def read_output(proc):
        for line in iter(proc.stdout.readline, ''):
            if line:
                with console_logs_lock:
                    console_logs.append(line.strip())
        proc.stdout.close()

    def get_console_logs():
        with console_logs_lock:
            return list(console_logs)

    process = None

    def send_command(command):
        if process is None or process.poll() is not None:
            return
        try:
            process.stdin.write(command + "\n")
            process.stdin.flush()
            with console_logs_lock:
                console_logs.append(f"> {command}")
        except (BrokenPipeError, OSError):
            with console_logs_lock:
                console_logs.append("Gagal mengirim perintah: stdin server tertutup")

    try:
        process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        
        server_process = psutil.Process(process.pid)

        log_thread = threading.Thread(target=read_output, args=(process,), daemon=True)
        log_thread.start()

        run_dashboard(process, server_process, get_console_logs, send_command, ram)
        process.wait()
        log_thread.join()
        if process.stdin:
            process.stdin.close()
    except KeyboardInterrupt:
        typer.secho(
            "\nMematikan server...",
            fg=typer.colors.YELLOW
        )

        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        typer.secho("Server berhasil di matikan", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()