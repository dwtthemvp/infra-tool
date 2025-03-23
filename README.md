# infra-status-cli

A simple, developer-friendly CLI tool for inspecting the health and status of ECS microservices running in AWS.  
Built with Python, Typer, and Boto3.

---

## 🔧 What It Does

✅ Lists all ECS services in a given environment  
✅ Describes a single ECS service with full status and rollout info  
✅ Displays output in a clean, color-coded terminal table  
✅ Fetches and displays recent CloudWatch Logs for a service  
✅ Supports multiple AWS environments using a YAML config file

---

## 📦 Installation

Clone the repo, set up a virtual environment, and install dependencies:

```bash
git clone <your-repo-url>
cd infra-status-cli
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🗂 Config File

Create a `config.yaml` file in the root directory.

```yaml
environments:
  dev:
    profile: dev-sso
    region: us-west-2
    ecs_cluster: dev-cluster-name

  prod:
    profile: prod-piv
    region: us-east-1
    ecs_cluster: prod-cluster-name
```

---

## 🚀 Usage

### List all ECS services in an environment:

```bash
python cli.py ecs --env dev
```

Shows all ECS services in the cluster along with:

- Desired / Running / Pending task count
- Task definition version
- Rollout status
- Color-coded health based on running state

---

### Describe an individual ECS service:

```bash
python cli.py service nginx --env dev
```

### Show recent logs for a service:

```bash
python cli.py service nginx --env dev --logs
```

Optional:
```bash
--log-lines 50  # default is 25
```

---

## 📘 Example Output

```
┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Service   ┃ Status  ┃ Desired┃ Running┃ Pending┃ Task Def   ┃ Rollout       ┃
┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ nginx     │ ACTIVE  │ 2      │ 2      │ 0      │ nginx:12   │ COMPLETED     │
│ logstash  │ ACTIVE  │ 1      │ 0      │ 1      │ logstash:9 │ IN_PROGRESS   │
└───────────┴─────────┴────────┴────────┴────────┴────────────┴───────────────┘
```

---

## 🔮 Roadmap

Planned features:

- `--watch` mode for real-time updates
- Log filtering via `--filter` pattern or keyword
- ALB and RDS inspection commands
- Audit subcommand for security/misconfig checks
- Terraform module summary
- OpenSearch dashboard health

---

## 🧪 Version

```bash
python cli.py version
```

Current: `infra-status-cli v0.1.0`

---

## 📄 License

MIT (or whatever you prefer)

---

## 💬 Contributions

Feel free to open issues or submit PRs — especially if you have AWS setups you want to monitor more easily!
