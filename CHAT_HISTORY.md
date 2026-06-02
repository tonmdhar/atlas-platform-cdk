# Chat History — Atlas Platform CDK Session 1

**Date:** 2026-05-31
**Project:** Atlas Platform v2 — CDK Edition (Python)

---

## Session Summary

Built Phase 1 of the Atlas Platform CDK project: CDK project setup + VPC/EKS constructs.

---

## Conversation Log

### 1. Read Project Plan

**User:** Read the PROJECT_PLAN.md plan
**Action:** Read and summarized the full project plan — a production-grade multi-environment EKS platform using AWS CDK with a single self-mutating pipeline (dev → staging → prod).

---

### 2. Language Decision

**User:** Why are we going with TypeScript?
**Discussion:** PROJECT_PLAN.md specified TypeScript but user was asked for preference.
**Decision:** User chose **Python** for CDK.

---

### 3. Build System Decision

**User:** What is the Config file used in Amazon CDK projects?
**Discussion:** Explained Brazil build system (internal, `Config` file in Ion format, version sets) vs standard open-source CDK (`requirements.txt`, pip, PyPI).
**Decision:** User chose **Standard CDK (open source)** — fits personal AWS account + GitHub + CodePipeline setup.

---

### 4. CDK Init — Non-Empty Directory Error

**User attempted:** `npx aws-cdk@latest init app --language python --generate-only`
**Error:**
```
Failed to validate directory /Users/tonmdhar/Desktop/atlas-platform-cdk: `cdk init` cannot be run in a non-empty directory!
Found 2 visible files in /Users/tonmdhar/Desktop/atlas-platform-cdk:
  - PROJECT_PLAN.md
  - README.md
```
**Fix:** Temporarily move PROJECT_PLAN.md and README.md to /tmp, run `cdk init`, then move them back.
**Outcome:** User resolved it successfully.

---

### 5. Git Repository Setup

**User:** Before we move forward, let's start with git repository creation & git push.
**Action:** User created GitHub repo `tonmdhar/atlas-platform-cdk` and pushed initial commit.
**Outcome:** Confirmed repo set up with `origin/main`.

---

### 6. Phase 1 — Creating Constructs

User requested guidance (manual file creation). Provided step-by-step instructions for:

1. Directory structure (`lib/config/`, `lib/constructs/`, `lib/stacks/`)
2. `lib/config/environments.py` — EnvironmentConfig dataclass + beta/gamma/prod configs
3. `lib/constructs/vpc_construct.py` — VPC + subnets + NAT
4. `lib/constructs/eks_construct.py` — EKS cluster + managed node group
5. `lib/stacks/infra_stack.py` — InfraStack composing VPC + EKS
6. `app.py` — CDK app entry point
7. `requirements.txt` — Python dependencies

---

### 7. Error: `NameError: name 'self' is not defined` (vpc_construct.py)

**Error:**
```
File "lib/constructs/vpc_construct.py", line 15, in __init__
    self,
    ^^^^
NameError: name 'self' is not defined
```

**Root Causes (3 typos):**
1. Line 9: `selfself` → `self` (parameter name typo)
2. Line 16: `ip_address=` → `ip_addresses=` (missing plural 's')
3. Line 21: `PRIVATE_WITH_Engress` → `PRIVATE_WITH_EGRESS` (capitalization typo)

**Outcome:** User fixed all three.

---

### 8. Error: `AttributeError: 'EnvironmentConfig' object has no attribute 'vpc_cidr'`

**Error:**
```
AttributeError: 'EnvironmentConfig' object has no attribute 'vpc_cidr'. Did you mean: 'vpc_cdr'?
```

**Root Cause:** Typo in `environments.py` — field named `vpc_cdr` instead of `vpc_cidr`.
**Fix:** Rename field in dataclass and all environment entries.
**Outcome:** User fixed it.

---

### 9. Error: `TypeError: Construct.__init__() got an unexpected keyword argument 'config'`

**Error:**
```
TypeError: Construct.__init__() got an unexpected keyword argument 'config'
```

**Root Cause:** `eks_construct.py` had `__init_` (single underscore) instead of `__init__` (double underscores). Python didn't recognize it as the constructor, so kwargs passed to parent `Construct.__init__()`.

**Fixes:**
1. `__init_` → `__init__` (method definition)
2. `super()._init_()` → `super().__init__()` (super call)
3. `config.node_instance_type` → `config.node_instance_types` (plural)

**Outcome:** User fixed all.

---

### 10. Error: `TypeError: Cluster.__init__() missing 1 required keyword-only argument: 'kubectl_layer'`

**Error:**
```
TypeError: Cluster.__init__() missing 1 required keyword-only argument: 'kubectl_layer'
```

**Root Cause:** Recent CDK versions require an explicit `kubectl_layer` for EKS clusters.

**Fix:**
1. Added `aws-cdk.lambda-layer-kubectl-v31` to `requirements.txt`
2. Imported `KubectlV31Layer` and passed to `eks.Cluster()`

**Outcome:** User fixed it.

---

### 11. Error: ADA Credentials — Invalid Role ARN

**Error:**
```
ada credentials update --account=733508956784, --provider=conduit --role=IibsAdminAccess-DO-NOT-DELETE --once
Failed to force refresh the credentials: unable to retrieve credentials: invalid role arn
```

**Root Cause:** Trailing comma after account number: `733508956784,`
**Fix:** Remove the comma: `--account=733508956784`
**Outcome:** User fixed it.

---

### 12. CDK Synth Successful ✅

User ran `cdk synth --context env=beta` successfully.

---

## Phase 1 Final State

**Completed:**
- CDK Python project initialized
- Environment config (beta/gamma/prod)
- VPC construct (subnets + NAT gateways)
- EKS construct (cluster + node group + kubectl layer + IRSA)
- InfraStack composing VPC + EKS
- `cdk synth` passing

**Environment naming:** User changed from dev/staging/prod → beta/gamma/prod

**Key files:**
```
atlas-platform-cdk/
├── app.py
├── cdk.json
├── requirements.txt
├── lib/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── environments.py
│   ├── constructs/
│   │   ├── __init__.py
│   │   ├── vpc_construct.py
│   │   └── eks_construct.py
│   └── stacks/
│       ├── __init__.py
│       └── infra_stack.py
└── tests/
```

---

## Next Steps

- Phase 1.5: DynamoDB Construct + Spring Boot Integration
- Phase 2: ECR + Secrets + Monitoring Constructs
- Phase 3: CDK Pipeline (Single Pipeline, Multi-Stage)

---

### 13. Git — Files to Track

**User:** Which files should I add to git?

**Add:**
- `app.py`, `cdk.json`, `requirements.txt`, `requirements-dev.txt`, `.gitignore`
- `lib/` (all constructs, stacks, config)
- `tests/`
- `PROJECT_PLAN.md`, `README.md`, `CHAT_HISTORY.md`

**Ignore (`.gitignore`):**
```
.venv/
cdk.out/
__pycache__/
*.py[cod]
.idea/
node_modules/
source.bat
cdk.context.json
*.egg-info/
dist/
```

**Note:** `source.bat` is a Windows-only venv activation script — not needed on macOS, added to `.gitignore`.

---

### 14. Git Commit

```bash
git add .gitignore app.py cdk.json requirements.txt requirements-dev.txt
git add lib/ tests/
git add PROJECT_PLAN.md README.md CHAT_HISTORY.md
git commit -m "feat: Phase 1 - CDK project with VPC and EKS constructs"
git push
```

---

### 15. Phase 1.5 — DynamoDB Construct + IRSA

**Constructs created:**
- `lib/constructs/dynamodb_construct.py` — DynamoDB table per env, on-demand billing, VPC gateway endpoint
- `lib/constructs/irsa_construct.py` — ServiceAccount with DynamoDB read/write permissions
- Updated `lib/stacks/infra_stack.py` — wired DynamoDB + IRSA
- Updated `app.py` — passes `env_name` to InfraStack

**Errors encountered:**
1. `ImportError: cannot import name 'DynamoDbConstruct'` — class was named `DynamoDBStack` instead of `DynamoDbConstruct`
2. `TypeError: Stack.__init__() got an unexpected keyword argument 'env_name'` — `env_name` wasn't declared before `**kwargs` in InfraStack's `__init__` signature

---

### 16. Phase 3 — CDK Pipeline (Single Pipeline, Multi-Stage)

**Files created:**
- `lib/stages/atlas_stage.py` — CDK Stage wrapping InfraStack
- `lib/stacks/pipeline_stack.py` — Self-mutating CodePipeline (GitHub source → Synth → Beta → Gamma → Manual Approval → Prod)
- Updated `app.py` — now only instantiates PipelineStack

**Errors encountered:**
1. `NameError: name 'InfraStack' is not defined` — old InfraStack import left in app.py after switching to PipelineStack
2. `TypeError: ShellStep.__init__() missing 1 required keyword-only argument: 'commands'` — `commands` parameter was missing from ShellStep

**Security decision:** Used `ENVIRONMENTS["beta"]` config for account/region instead of hardcoding values in app.py.

---

### 17. Phase 2 — ECR + Secrets + Monitoring Constructs

**Files created:**
- `lib/constructs/ecr_construct.py` — ECR repo with lifecycle rules
- `lib/constructs/secrets_construct.py` — Secrets Manager + IRSA for secrets access
- `lib/constructs/monitoring_construct.py` — CloudWatch alarms (CPU/Memory), dashboard, SNS alerts

**Errors encountered:**
1. `TypeError: LifecycleRule.__init__() got an unexpected keyword argument 'max_image_age_days'` — correct param is `max_image_age=Duration.days(1)`
2. `TypeError: Duration() takes no arguments` — CDK Python uses `Duration.days(1)` not `Duration(days=1)`
3. `AnyTagStatusRuleMustHaveHighestPriority` — rule with `max_image_count` (implicitly TagStatus.ANY) must have highest priority number. Swapped priorities.
4. `AttributeError: 'SecretsConstruct' object has no attribute 'app_secret'` — variable name mismatch between definition and usage

---

### 18. Phase 5 — Spring Boot App + Docker (Automated)

**Files created (automated by Wasabi):**
```
app/
├── pom.xml                          # Spring Boot 3.3, Java 21, DynamoDB SDK, Lombok
├── Dockerfile                       # Multi-stage (amazoncorretto:21-alpine3.21, non-root)
└── src/main/
    ├── java/com/atlas/platform/
    │   ├── AtlasPlatformApplication.java
    │   ├── config/DynamoDbConfig.java
    │   ├── model/Item.java
    │   ├── service/ItemService.java
    │   └── controller/
    │       ├── ItemController.java   # POST/GET/PUT/DELETE /api/items
    │       └── InfoController.java   # GET /api/info
    └── resources/
        ├── application.yml           # Default (port 8080, actuator)
        ├── application-beta.yml      # Table: atlas-platform-beta-items
        ├── application-gamma.yml     # Table: atlas-platform-gamma-items
        └── application-prod.yml      # Table: atlas-platform-prod-items
```

**Key features:** Non-root user (1001), MaxRAMPercentage=75%, --platform linux/amd64, actuator probes.

---

### 19. Phase 4 — Kubernetes Manifests + Buildspecs (Automated)

**Files created (automated by Wasabi):**
```
k8s/
├── base/
│   ├── kustomization.yaml, namespace.yaml, deployment.yaml
│   ├── service.yaml, hpa.yaml, pdb.yaml
├── overlays/
│   ├── beta/kustomization.yaml
│   ├── gamma/kustomization.yaml
│   └── prod/kustomization.yaml
buildspecs/
├── buildspec-build.yml              # Maven + Docker + ECR push
├── buildspec-deploy.yml             # kubectl apply -k + rollout wait
├── buildspec-smoke-test.yml         # Health + pod checks
└── buildspec-integration-test.yml   # Full CRUD + load test
```

**Key features:** initialDelaySeconds=60, runAsNonRoot, namespace in patches, HPA 2-6 pods.

---

## Updated Project Status

| Phase | Status |
|-------|--------|
| Phase 1: CDK Setup + VPC/EKS | ✅ Complete |
| Phase 1.5: DynamoDB + IRSA | ✅ Complete |
| Phase 2: ECR + Secrets + Monitoring | ✅ Complete |
| Phase 3: CDK Pipeline | ✅ Complete |
| Phase 4: K8s Manifests + Buildspecs | ✅ Complete |
| Phase 5: Spring Boot App + Docker | ✅ Complete |
| Phase 6: Integration Tests | ✅ Complete |
| Pipeline Deployment | ⏳ In Progress |

---

## Pipeline Deployment Errors & Fixes

### 20. CDK Bootstrap Required

**Error:**
```
SSM parameter /cdk-bootstrap/hnb659fds/version not found. Has the environment been bootstrapped?
```

**Fix:** Run `cdk bootstrap aws://733508956784/us-east-1` (one-time per account/region).

---

### 21. ModuleNotFoundError: No module named 'aws_cdk'

**Error:**
```
ModuleNotFoundError: No module named 'aws_cdk'
```

**Root Cause:** Virtual environment not activated.
**Fix:** Run `source .venv/bin/activate` before any `cdk` commands.

---

### 22. Pipeline Not Visible in AWS Console

**Root Cause:** `cdk bootstrap` only creates the CDK toolkit (S3, IAM roles). The pipeline itself still needs to be deployed.
**Fix:** Run `cdk deploy AtlasPlatform-Pipeline`.

---

### 23. Pipeline Synth — `npm cdk synth` Wrong Command

**Error:**
```
Command did not exit successfully npm cdk synth exit status 1
```

**Root Cause:** ShellStep had `npm cdk synth` instead of `npx cdk synth`.
**Fix:** Changed `commands=["npx cdk synth"]` in pipeline_stack.py.

---

### 24. Pipeline Synth — `ec2:DescribeAvailabilityZones` Not Authorized

**Error:**
```
User is not authorized to perform: ec2:DescribeAvailabilityZones because no identity-based policy allows the ec2:DescribeAvailabilityZones action
```

**Root Cause:** The VPC construct triggers an AZ lookup during `cdk synth`, and the CodeBuild synth role doesn't have the permission.

**Fixes applied (both needed):**
1. Changed `max_azs=len(config.azs)` → `availability_zones=config.azs` in `vpc_construct.py` (avoids lookup)
2. Added `synth_code_build_defaults` with `ec2:DescribeAvailabilityZones` policy to `pipeline_stack.py` (grants permission for any remaining lookups)

```python
synth_code_build_defaults=pipelines.CodeBuildOptions(
    role_policy=[
        iam.PolicyStatement(
            actions=["ec2:DescribeAvailabilityZones"],
            resources=["*"],
        ),
    ],
),
```

**Important:** Must `cdk deploy AtlasPlatform-Pipeline` locally first (to update IAM role), then `git push` for the pipeline to pick up code changes.

---

### 25. CodeStar Connection — Pipeline Not Triggering on Push

**Root Cause:** The GitHub App associated with the CodeStar connection didn't have access to the `atlas-platform-cdk` repo.

**Fix:**
1. GitHub → Settings → Applications → "AWS Connector for GitHub" → Configure
2. Under "Repository access" → add `atlas-platform-cdk`
3. This created a new connection with ARN: `arn:aws:codeconnections:us-east-1:733508956784:connection/4baa5052-881b-4c4b-8b46-22d0bd0ad19a`
4. Updated `pipeline_stack.py` with the new connection ARN

---

### 26. Pipeline Synth — Permission Still Failing After vpc_construct Fix

**Root Cause:** The `vpc_construct.py` fix was applied locally but not pushed to GitHub. The pipeline runs code from the remote repo, not local.

**Lesson:** Always verify changes are committed AND pushed:
```bash
git status
git add <file>
git commit -m "fix: description"
git push
```

---

## Lessons Learned — Pipeline Deployment

| Lesson | Detail |
|--------|--------|
| `cdk bootstrap` is one-time | Creates CDKToolkit stack (S3, IAM, SSM) |
| `cdk deploy` ≠ `cdk bootstrap` | Bootstrap = toolkit, Deploy = your stacks |
| Activate venv every session | `source .venv/bin/activate` |
| Pipeline runs GitHub code | Local fixes must be pushed to take effect |
| CodeBuild synth role has limited perms | Add policies via `synth_code_build_defaults` |
| CodeStar connection needs repo access | GitHub App must have access to the specific repo |
| Self-mutating pipeline needs initial deploy | First `cdk deploy`, then pipeline handles itself |
