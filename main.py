import subprocess
import time

import psutil
import requests as rq
import typer
from typer import Option

app = typer.Typer()

@app.command()
def respon(url: str = Option(..., "--url", "-u", help="URL target yang ingin dicek")) -> str:
    res = rq.get(url)
    if res.status_code == 200:
        return print("Jaringan terkoneksi")
    else:
        return print("500, atau error lain")

@app.command()
def connectServer(
    ram: str = Option("2G", "--ram", "-r", help="Masukan jumlah ram yang ingin dialokasi"),
    jar: str = Option(..., "--jar", "-j", help="Server jar"),
):
    typer.echo("Menyiapkan server....")
    typer.echo(f"Alokasi ram: {ram}")
    typer.echo(f"file server: {jar}")

    cmd = ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", jar, "nogui"]

    try:
        typer.secho("Berhasil menyambungkan ( CTRL + C )")

        process = subprocess.Popen(cmd)
        server_process = psutil.Process(process.pid)

        while process.poll() is None:
            try:
                
                mem_info = server_process.memory_info()
                ram_used_mb = mem_info.rss / (1024 * 1024)
                ram_used_gb = ram_used_mb / 1024

                print(
                    f"\r[Monitor RAM] Terpakai: {ram_used_mb:.2f} MB ({ram_used_gb:.2f}"
                    " GB)   ",
                    end="",
                    flush=True,
                )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(1)

        process.wait()
    except KeyboardInterrupt:
        typer.secho("Mematikan server", fg=typer.colors.YELLOW)
        process.terminate()
        process.wait()
        typer.secho("Server berhasil dimatikan", fg=typer.colors.RED)

if __name__ == "__main__":
    app()