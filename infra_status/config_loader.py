import yaml


def load_config():
    with open("config.yaml") as stream:
        try:
            data = yaml.safe_load(stream)
            return data['environments']
        except yaml.YAMLError as exc:
            raise RuntimeError(f"Error loading config file: {exc}")


def get_env(env_name):
    config = load_config()
    if env_name not in config:
        raise ValueError(f"Environment {env_name} not in config.yaml")
    return config[env_name]

