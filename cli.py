import typer
from infra_status.ecs.ecs_cmd import ecs_app
from infra_status.version_cmd import version_app
from infra_status.alb.alb_cmd import alb_app

app = typer.Typer()
app.add_typer(ecs_app, name="ecs")
app.add_typer(version_app)
app.add_typer(alb_app,name="alb")


if __name__ == "__main__":
    app()
