import typer
import questionary
from datetime import datetime, timedelta
from rich.table import Table
from rich.console import Console
import datetime

from infra_status.config_loader import get_env
from infra_status.aws_session import aws_session
from infra_status.alb.alb_utils import resolve_alb

alb_app = typer.Typer()


@alb_app.command("select")
def select_alb(
    env: str = typer.Option(..., help="Environment name (e.g., dev, prod)"),
    alb: str = typer.Option(None, help="Optional ALB name to use directly"),
):
    """
    Select and display info about an ALB.
    """
    config = get_env(env)
    session = aws_session(env)
    elbv2 = session.client("elbv2")

    response = elbv2.describe_load_balancers()
    load_balancers = response["LoadBalancers"]

    if not load_balancers:
        typer.echo("No load balancers found.")
        raise typer.Exit()

    alb_map = {lb["LoadBalancerName"]: lb for lb in load_balancers}

    if alb:
        if alb not in alb_map:
            typer.echo(f"❌ Load balancer '{alb}' not found.")
            raise typer.Exit()
        selected = alb
    else:
        selected = questionary.select("Select a Load Balancer:", choices=list(alb_map.keys())).ask()

    selected_alb = alb_map[selected]

    typer.echo(f"✔️  Selected ALB: {selected}")
    typer.echo(f"  - DNS Name: {selected_alb['DNSName']}")
    typer.echo(f"  - Scheme: {selected_alb['Scheme']}")
    typer.echo(f"  - Type: {selected_alb['Type']}")
    typer.echo(f"  - State: {selected_alb['State']['Code']}")


@alb_app.command("metrics")
def alb_metrics(
    env: str = typer.Option(..., help="Environment name (e.g., dev, prod)"),
    alb: str = typer.Option(None, help="Optional ALB name to use directly"),
):
    """
    Show recent metrics for a given Application Load Balancer.
    """
    config = get_env(env)
    session = aws_session(env)
    cloudwatch = session.client("cloudwatch")

    alb_name, cw_name, alb_arn = resolve_alb(session, alb)

    metrics = [
        ("RequestCount", "Sum"),
        ("HTTPCode_ELB_5XX_Count", "Sum"),
        ("HTTPCode_Target_5XX_Count", "Sum"),
        ("TargetResponseTime", "Average"),
    ]

    now = datetime.datetime.now(datetime.UTC)
    start_time = now - timedelta(minutes=15)

    table = Table(title=f"Metrics for ALB: {alb_name}")
    table.add_column("Metric")
    table.add_column("Stat")
    table.add_column("Value")
    table.add_column("Unit")

    for metric_name, stat in metrics:
        response = cloudwatch.get_metric_statistics(
            Namespace="AWS/ApplicationELB",
            MetricName=metric_name,
            Dimensions=[{"Name": "LoadBalancer", "Value": cw_name}],
            StartTime=start_time,
            EndTime=now,
            Period=300,
            Statistics=[stat]
        )

        datapoints = response.get("Datapoints", [])
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x["Timestamp"])[-1]
            value = f"{latest[stat]:.2f}"
            unit = latest["Unit"]
        else:
            value = "N/A"
            unit = "-"

        table.add_row(metric_name, stat, value, unit)

    console = Console()
    console.print(table)
