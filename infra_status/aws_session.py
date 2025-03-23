import boto3
from infra_status.config_loader import get_env


def aws_session(env):
    config = get_env(env)

    if "profile" in config:
        return boto3.Session(profile_name=config["profile"], region_name=config["region"])
    else:
        return boto3.Session(region_name=config["region"])


def get_boto_clients(env, *services):
    session = aws_session(env)
    return {svc: session.client(svc) for svc in services}
