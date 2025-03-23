from rich.console import Console
from rich.table import Table


def print_service_table(services):
    console = Console()
    table = Table(title="ECS Service Status", header_style="bold magenta")

    table.add_column("Service")
    table.add_column("Status")
    table.add_column("Desired", justify="right")
    table.add_column("Running", justify="right")
    table.add_column("Pending", justify="right")
    table.add_column("Task Def")
    table.add_column("Rollout")

    for svc in services:
        desired = svc["desired"]
        running = svc["running"]
        rollout = svc["rollout_state"]

        # Color coding
        if rollout == "IN_PROGRESS":
            style = "yellow"
        elif running == desired:
            style = "green"
        elif running > 0:
            style = "yellow"
        else:
            style = "red"

        table.add_row(
            svc["name"],
            svc["status"],
            str(desired),
            str(running),
            str(svc["pending"]),
            svc["task_def"],
            svc["rollout_state"],
            style=style
        )

    console.print(table)
