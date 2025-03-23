import typer
from infra_status.aws_session import aws_session
from infra_status.ecs.ecs_utils import resolve_cluster
from infra_status.rich_output import print_service_table


def describe_services(
    env: str = typer.Option(...),
    cluster: str = typer.Option(None, help="ECS cluster name (optional)"),
):
    session = aws_session(env)
    ecs = session.client("ecs")

    cluster_name, cluster_arn = resolve_cluster(session, cluster)
    response = ecs.list_services(cluster=cluster_arn)
    service_arns = response["serviceArns"]

    if not service_arns:
        return

    details = ecs.describe_services(cluster=cluster_arn, services=service_arns)
    services = [
        {
            "name": svc["serviceName"],
            "status": svc["status"],
            "desired": svc["desiredCount"],
            "running": svc["runningCount"],
            "pending": svc["pendingCount"],
            "task_def": svc["taskDefinition"].split("/")[-1],
            "rollout_state": svc.get("deployments", [{}])[0].get("rolloutState", "-"),
        }
        for svc in details["services"]
    ]

    print_service_table(services)
