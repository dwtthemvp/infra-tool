from rich.console import Console
from rich.table import Table
import typer

from infra_status.aws_session import aws_session
from infra_status.ecs.ecs_utils import resolve_cluster
from infra_status.ecs.ecs_utils import resolve_service


def monitor_deployments(
    env: str = typer.Option(...),
    cluster: str = typer.Option(None),
    name: str = typer.Option(None),
):
    session = aws_session(env)
    ecs = session.client("ecs")
    console = Console()

    cluster_name, cluster_arn = resolve_cluster(session, cluster)
    if not name:
        name = resolve_service(session, cluster_arn)

    response = ecs.describe_services(cluster=cluster_arn, services=[name])
    service = response["services"][0]
    deployments = service.get("deployments", [])

    if not deployments:
        typer.echo("⚠️  No deployments found.")
        return

    table = Table(title=f"[bold blue]Deployments for ECS service: {name}[/]")
    table.add_column("Deployment ID", style="dim")
    table.add_column("Status")
    table.add_column("Rollout")
    table.add_column("Desired", justify="right")
    table.add_column("Running", justify="right")
    table.add_column("Pending", justify="right")
    table.add_column("Created", style="cyan")
    table.add_column("Updated", style="cyan")

    for dep in deployments:
        status = dep.get("status", "-")
        rollout = dep.get("rolloutState", "-")
        status_style = "bold magenta" if status == "PRIMARY" else "dim"
        rollout_style = {
            "COMPLETED": "green",
            "IN_PROGRESS": "yellow",
            "FAILED": "red"
        }.get(rollout, "dim")

        created = dep.get("createdAt")
        updated = dep.get("updatedAt")
        created_fmt = created.strftime("%Y-%m-%d %H:%M:%S") if created else "-"
        updated_fmt = updated.strftime("%Y-%m-%d %H:%M:%S") if updated else "-"

        table.add_row(
            dep.get("id", "-"),
            f"[{status_style}]{status}[/{status_style}]",
            f"[{rollout_style}]{rollout}[/{rollout_style}]",
            str(dep.get("desiredCount", 0)),
            str(dep.get("runningCount", 0)),
            str(dep.get("pendingCount", 0)),
            created_fmt,
            updated_fmt
        )

    console.print(table)
