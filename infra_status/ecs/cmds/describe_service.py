import time
from datetime import datetime
import typer
from rich.console import Console
import questionary

from infra_status.aws_session import aws_session
from infra_status.rich_output import print_service_table
from infra_status.ecs.ecs_utils import resolve_cluster
from infra_status.ecs.ecs_utils import resolve_service


def describe_service(
    name: str = typer.Option(None),
    env: str = typer.Option(...),
    cluster: str = typer.Option(None),
    logs: bool = typer.Option(False),
    log_lines: int = typer.Option(25),
    task_id: str = typer.Option(None),
    all: bool = typer.Option(False),
    container: str = typer.Option(None),
    follow: bool = typer.Option(False),
    multi: bool = typer.Option(False),
):
    session = aws_session(env)
    ecs = session.client("ecs")

    cluster_name, cluster_arn = resolve_cluster(session, cluster)
    if not name:
        name = resolve_service(session, cluster_arn)

    response = ecs.describe_services(cluster=cluster_arn, services=[name])
    service = response["services"][0]

    svc_data = {
        "name": service["serviceName"],
        "status": service["status"],
        "desired": service["desiredCount"],
        "running": service["runningCount"],
        "pending": service["pendingCount"],
        "task_def": service["taskDefinition"].split("/")[-1],
        "rollout_state": service.get("deployments", [{}])[0].get("rolloutState", "-"),
    }

    print_service_table([svc_data])

    if not logs:
        confirm = questionary.confirm("Do you want to view logs for this service?").ask()
        if not confirm:
            return

        log_lines = questionary.text(
            "How many log lines do you want to show?",
            default=str(log_lines),
            validate=lambda val: val.isdigit() and int(val) > 0
        ).ask()

        log_lines = int(log_lines)

    logs_client = session.client("logs")
    task_def = ecs.describe_task_definition(taskDefinition=service["taskDefinition"])["taskDefinition"]

    tasks = ecs.list_tasks(cluster=cluster_arn, serviceName=name)["taskArns"]
    if not tasks:
        typer.echo("⚠️  No running tasks found.")
        return

    task_ids = [t.split("/")[-1] for t in tasks]
    selected_tasks = []

    if task_id:
        if task_id not in task_ids:
            typer.echo(f"❌ Task ID '{task_id}' not found.")
            return
        selected_tasks = [task_id]
    elif all:
        selected_tasks = task_ids
    elif len(task_ids) == 1:
        selected_tasks = [task_ids[0]]
    else:
        selected = questionary.select("Multiple running tasks found. Select one:", choices=task_ids).ask()
        selected_tasks = [selected]

    for tid in selected_tasks:
        console = Console()
        container_defs = task_def["containerDefinitions"]

        if container:
            containers = [c for c in container_defs if c["name"] == container]
            if not containers:
                typer.echo(f"❌ No container named '{container}' found.")
                return
        else:
            container_names = [c["name"] for c in container_defs]
            if multi:
                selected = questionary.checkbox("Select container(s):", choices=container_names).ask()
                if not selected:
                    typer.echo("⚠️  No containers selected.")
                    return
                containers = [c for c in container_defs if c["name"] in selected]
            else:
                selected = questionary.select("Select a container:", choices=container_names).ask()
                containers = [c for c in container_defs if c["name"] == selected]

        for container_def in containers:
            cname = container_def["name"]
            options = container_def.get("logConfiguration", {}).get("options", {})
            group = options.get("awslogs-group")
            prefix = options.get("awslogs-stream-prefix")

            if not group or not prefix:
                typer.echo(f"⚠️  No logs configured for container: {cname}")
                continue

            log_stream = f"{prefix}/{cname}/{tid}"
            console.print(f"\n📜 [green]Container:[/] {cname} | [yellow]Task ID:[/] {tid}")
            console.print(f"[blue]Log stream:[/] {log_stream}")

            try:
                while True:
                    events = logs_client.get_log_events(
                        logGroupName=group,
                        logStreamName=log_stream,
                        limit=log_lines,
                        startFromHead=False
                    )["events"]

                    for e in events:
                        ts = datetime.utcfromtimestamp(e["timestamp"] / 1000).isoformat()
                        print(f"[{ts}] {e['message']}")

                    if not follow:
                        break

                    time.sleep(3)

            except logs_client.exceptions.ResourceNotFoundException:
                typer.echo(f"⚠️  Log stream not found: {log_stream}")
