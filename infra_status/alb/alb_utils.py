import questionary

def resolve_alb(session, alb_name=None):
    """
    Returns: (LoadBalancerName, CloudWatchDimensionValue, ARN)
    """
    elbv2 = session.client("elbv2")
    response = elbv2.describe_load_balancers()
    lbs = response["LoadBalancers"]

    alb_map = {}
    for lb in lbs:
        name = lb["LoadBalancerName"]
        arn = lb["LoadBalancerArn"]
        cw_name = arn.split("loadbalancer/")[-1]  # ex: app/my-alb/abc123
        alb_map[name] = {
            "arn": arn,
            "cw_name": cw_name,
        }

    if alb_name:
        if alb_name not in alb_map:
            raise ValueError(f"Load balancer '{alb_name}' not found.")
        return alb_name, alb_map[alb_name]["cw_name"], alb_map[alb_name]["arn"]

    selected = questionary.select(
        "Select a Load Balancer:",
        choices=list(alb_map.keys())
    ).ask()

    return selected, alb_map[selected]["cw_name"], alb_map[selected]["arn"]
