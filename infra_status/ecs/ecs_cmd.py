import typer
from infra_status.ecs.cmds.describe_service import describe_service
from infra_status.ecs.cmds.describe_services import describe_services
from infra_status.ecs.cmds.watch_services import watch_services
from infra_status.ecs.cmds.get_metrics import get_service_metrics
from infra_status.ecs.cmds.monitor_deployments import monitor_deployments
ecs_app = typer.Typer()

ecs_app.command("describe-services")(describe_services)
ecs_app.command("describe-service")(describe_service)
ecs_app.command("watch-service")(watch_services)
ecs_app.command("get-metrics")(get_service_metrics)
ecs_app.command("monitor-deployments")(monitor_deployments)
