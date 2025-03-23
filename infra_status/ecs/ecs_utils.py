import questionary
import typer


def resolve_cluster(session, cluster_name=None):
    ecs = session.client("ecs")
    cluster_arns = ecs.list_clusters()["clusterArns"]

    if not cluster_arns:
        typer.echo(f"⚠️  No ECS clusters found!")
        raise typer.Exit(code=0)

    cluster_map = {arn.split("/")[-1]: arn for arn in cluster_arns}

    if cluster_name:
        if cluster_name not in cluster_map:
            raise ValueError(f"Cluster '{cluster_name}' not found.")
        return cluster_name, cluster_map[cluster_name]

    selected = questionary.select(
        "Select an ECS cluster:",
        choices=list(cluster_map.keys())
    ).ask()

    return selected, cluster_map[selected]


def resolve_service(session, cluster_arn, allow_all: bool = False):
    """
    Prompt the user to select an ECS service in the given cluster.
    If allow_all=True, includes an "All services" option.
    Returns: single service name OR list of all service names.
    """
    ecs = session.client("ecs")
    response = ecs.list_services(cluster=cluster_arn)
    service_arns = response["serviceArns"]

    if not service_arns:
        typer.echo(f"⚠️  No ECS services found in cluster: {cluster_arn}")
        raise typer.Exit(code=0)

    service_names = [arn.split("/")[-1] for arn in service_arns]

    if allow_all:
        service_names.insert(0, "[ALL SERVICES]")

    selected = questionary.select(
        "Select an ECS service:",
        choices=service_names
    ).ask()

    if selected == "[ALL SERVICES]":
        return service_names[1:]
    return selected
