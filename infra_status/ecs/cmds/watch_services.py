import os
import time
from rich.console import Console
import typer

from infra_status.config_loader import get_env
from infra_status.aws_session import aws_session
from infra_status.rich_output import print_service_table
from infra_status.ecs.ecs_utils import resolve_cluster
from infra_status.ecs.ecs_utils import resolve_service


def watch_services(
    env: str = typer.Option(...),
    cluster: str = typer.Option(None),
    name: str = typer.Option(None),
    interval: int = typer.Option(5),
):
    session = aws_session(env)
    ecs = session.client("ecs")
    console = Console()

    cluster_name, cluster_arn = resolve_cluster(session, cluster)

    if not name:
        name = resolve_service(session, cluster_arn, allow_all=True)
    if isinstance(name, str):
        name = [name]

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            console.rule(f"[green]ECS Service Status - {env} / {cluster_name}[/]")

            arns = ecs.list_services(cluster=cluster_arn)["serviceArns"]
            matched = [arn for arn in arns if arn.split("/")[-1] in name]
            if not matched:
                console.print("No matching services.")
                time.sleep(interval)
                continue

            details = ecs.describe_services(cluster=cluster_arn, services=matched)
            services = [
                {
                    "name": s["serviceName"],
                    "status": s["status"],
                    "desired": s["desiredCount"],
                    "running": s["runningCount"],
                    "pending": s["pendingCount"],
                    "task_def": s["taskDefinition"].split("/")[-1],
                    "rollout_state": s.get("deployments", [{}])[0].get("rolloutState", "-"),
                }
                for s in details["services"]
            ]

            print_service_table(services)
            console.print(f"\n🔁 Refreshing in {interval} seconds... (Ctrl+C to quit)")
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n👋 Exiting watch mode.")
