from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
import typer

from infra_status.config_loader import get_env
from infra_status.aws_session import aws_session
from infra_status.ecs.ecs_utils import resolve_cluster
from infra_status.ecs.ecs_utils import resolve_service


def get_service_metrics(
    name: str = typer.Option(None, help="Name of the ECS service (optional)"),
    env: str = typer.Option(...),
    cluster: str = typer.Option(None)
):
    config = get_env(env)
    session = aws_session(env)
    cloudwatch = session.client("cloudwatch")

    cluster_name, cluster_arn = resolve_cluster(session, cluster)
    if not name:
        name = resolve_service(session, cluster_arn)

    metrics = [
        ("CPUUtilization", "Average"),
        ("MemoryUtilization", "Average"),
        ("RunningTaskCount", "Average"),
        ("PendingTaskCount", "Average"),
    ]

    now = datetime.utcnow()
    start_time = now - timedelta(minutes=15)

    table = Table(title=f"[bold blue]📊 Metrics for ECS Service: {name}[/]")
    table.add_column("Metric", style="bold white")
    table.add_column("Stat", style="dim")
    table.add_column("Value", justify="right")
    table.add_column("Unit", style="dim")

    for metric_name, stat in metrics:
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/ECS",
            MetricName=metric_name,
            Dimensions=[
                {"Name": "ClusterName", "Value": cluster_name},
                {"Name": "ServiceName", "Value": name}
            ],
            StartTime=start_time,
            EndTime=now,
            Period=300,
            Statistics=[stat]
        )

        datapoints = response.get("Datapoints", [])
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x["Timestamp"])[-1]
            value = latest[stat]
            unit = latest["Unit"]

            # Color logic
            if metric_name == "CPUUtilization":
                value_style = "green" if value < 70 else "yellow" if value < 90 else "red"
            elif metric_name == "MemoryUtilization":
                value_style = "green" if value < 75 else "yellow" if value < 90 else "red"
            elif metric_name == "PendingTaskCount":
                value_style = "green" if value == 0 else "red"
            else:
                value_style = "white"

            value_str = f"[{value_style}]{value:.2f}[/{value_style}]"
        else:
            value_str = "[dim]N/A[/dim]"
            unit = "-"

        table.add_row(metric_name, stat, value_str, unit)

    console = Console()
    console.print(table)

