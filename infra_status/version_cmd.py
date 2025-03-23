import typer

version_app = typer.Typer()


@version_app.command("version")
def show_version():
    typer.echo("infra-status-cli v0.1.0")
