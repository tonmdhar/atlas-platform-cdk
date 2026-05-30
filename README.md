# Atlas Platform v2 — CDK Edition

A production-grade multi-environment EKS platform on AWS built with CDK (TypeScript), featuring a **single self-mutating pipeline** that promotes through stages (dev → staging → prod) with integration tests between each stage and DynamoDB-backed CRUD APIs.

## Architecture

```
┌─ GitHub (main branch) ────────────────────────────────────────────────┐
│  git push                                                               │
└──────┬──────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─── CDK Pipeline (Self-Mutating) ──────────────────────────────────────┐
│                                                                         │
│  ┌─────────┐   ┌──────────┐   ┌────────────┐   ┌──────────────────┐   │
│  │ SOURCE  │──►│  BUILD   │──►│ DEPLOY DEV │──►│ DEPLOY STAGING   │   │
│  │ GitHub  │   │ Synth    │   │ + Smoke    │   │ + Integration    │   │
│  │         │   │ Docker   │   │   Tests    │   │   Tests          │   │
│  └─────────┘   │ ECR Push │   └────────────┘   └────────┬─────────┘   │
│                └──────────┘                              │             │
│                                                          ▼             │
│                                              ┌──────────────────┐      │
│                                              │ MANUAL APPROVAL  │      │
│                                              │  ⛔ Human gate   │      │
│                                              └────────┬─────────┘      │
│                                                       │                │
│                                                       ▼                │
│                                              ┌──────────────────┐      │
│                                              │  DEPLOY PROD     │      │
│                                              │  + Smoke Tests   │      │
│                                              │  + Alarm Check   │      │
│                                              └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─ EKS Clusters (per environment) ──────────────────────────────────────┐
│                                                                         │
│  ┌─ Private Subnets ─────────────────────────────────────────────┐     │
│  │  Pods → Spring Boot App → DynamoDB (via VPC Endpoint)          │     │
│  │  HPA auto-scales │ PDB protects │ Probes monitor health        │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  NAT Gateway → Outbound (ECR, CloudWatch, Secrets Manager)              │
└─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─ Observability ───────────────────────────────────────────────────────┐
│  CloudWatch Container Insights → Alarms → SNS → Email                   │
│  Dashboard: CPU, Memory, Pods, Network, DynamoDB Read/Write             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Differences from v1 (Terraform Version)

| Aspect | v1 (multi-pipeline-eks) | v2 (atlas-platform-cdk) |
|---|---|---|
| IaC Tool | Terraform (HCL) | AWS CDK (TypeScript) |
| Pipeline | Separate pipeline per env | **Single pipeline, multi-stage** |
| Promotion | Independent (parallel) | Sequential (dev → staging → prod) |
| Testing | None | **Smoke + Integration tests** |
| Database | None | **DynamoDB (CRUD API)** |
| Approval | Prod only | Between staging → prod |
| State | S3 + DynamoDB | CloudFormation (managed by AWS) |
| Reusability | Terraform modules | CDK Constructs (L3, typed) |

## Tech Stack

| Category | Technology |
|---|---|
| Cloud | AWS (EKS, ECR, VPC, CodePipeline, CodeBuild, DynamoDB, Secrets Manager, CloudWatch, SNS) |
| IaC | AWS CDK (TypeScript) |
| Container | Docker (multi-stage, amazoncorretto:21-alpine3.21) |
| Orchestration | Kubernetes (EKS) with Kustomize overlays |
| Application | Java 21, Spring Boot 3.3, AWS SDK v2, Spring Actuator |
| Database | DynamoDB (on-demand, per-env tables, VPC endpoint) |
| CI/CD | CDK Pipelines (self-mutating) + CodeBuild |
| Testing | Smoke tests (dev/prod), Integration tests (staging), k6 load tests |
| Monitoring | CloudWatch Container Insights, Alarms, Dashboards, SNS |
| Security | Private subnets, IRSA, non-root containers, VPC endpoints, Secrets Manager |

## Project Structure

```
atlas-platform-cdk/
├── bin/
│   └── atlas-platform.ts              # CDK app entry point
├── lib/
│   ├── constructs/                    # Reusable L3 constructs
│   │   ├── vpc-construct.ts           # VPC + subnets + NAT
│   │   ├── eks-construct.ts           # EKS cluster + node groups + IAM
│   │   ├── ecr-construct.ts           # ECR repository + lifecycle
│   │   ├── dynamodb-construct.ts      # DynamoDB table + VPC endpoint + IRSA
│   │   ├── secrets-construct.ts       # Secrets Manager + IRSA policy
│   │   ├── monitoring-construct.ts    # CloudWatch alarms + dashboard + SNS
│   │   └── codebuild-construct.ts     # CodeBuild projects
│   ├── stages/
│   │   └── atlas-stage.ts             # CDK Stage (one per environment)
│   ├── stacks/
│   │   ├── infra-stack.ts             # VPC + EKS + ECR + DynamoDB + Secrets
│   │   ├── pipeline-stack.ts          # CDK Pipeline definition
│   │   └── monitoring-stack.ts        # CloudWatch + SNS
│   └── config/
│       └── environments.ts            # Per-env config (CIDRs, sizes, table names)
├── test/
│   ├── unit/                          # CDK construct unit tests
│   │   ├── vpc-construct.test.ts
│   │   ├── eks-construct.test.ts
│   │   └── pipeline-stack.test.ts
│   └── integration/                   # Integration tests (run in pipeline)
│       ├── smoke-tests.sh             # Health check, API validation
│       ├── api-tests.ts               # Full CRUD integration tests
│       └── load-test.sh               # k6 load testing
├── k8s/                               # Kustomize manifests
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── hpa.yaml
│   │   └── pdb.yaml
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── app/                               # Spring Boot application
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/main/
│       ├── java/com/atlas/platform/
│       │   ├── AtlasPlatformApplication.java
│       │   ├── config/AppConfig.java
│       │   ├── controller/
│       │   │   ├── HealthController.java
│       │   │   └── ItemController.java    # DynamoDB CRUD
│       │   ├── model/Item.java
│       │   └── repository/ItemRepository.java
│       └── resources/
│           ├── application.yml
│           ├── application-dev.yml
│           ├── application-staging.yml
│           └── application-prod.yml
├── buildspecs/
│   ├── buildspec-build.yml            # Docker build + ECR push
│   ├── buildspec-deploy.yml           # kubectl apply to EKS
│   ├── buildspec-smoke-test.yml       # Post-deploy health validation
│   └── buildspec-integration-test.yml # Full API + load tests (staging)
├── cdk.json
├── package.json
├── tsconfig.json
└── PROJECT_PLAN.md
```

## Environment Comparison

| | Dev | Staging | Prod |
|---|---|---|---|
| VPC CIDR | 10.10.0.0/16 | 10.20.0.0/16 | 10.30.0.0/16 |
| Availability Zones | 2 | 2 | 3 |
| NAT Gateway | Single | Single | Multi (one per AZ) |
| Node Type | t3.medium | t3.large | t3.large |
| Node Count | 2 (max 3) | 2 (max 3) | 3 (max 6) |
| HPA Range | 1-3 pods | 2-4 pods | 3-6 pods |
| DynamoDB Table | atlas-dev-items | atlas-staging-items | atlas-prod-items |
| DynamoDB Mode | On-demand | On-demand | On-demand |
| Pipeline Stage | Auto-promote | Auto-promote | Manual approval |
| Post-Deploy Tests | Smoke tests | Integration + Load | Smoke tests |

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/actuator/health/liveness` | GET | Kubernetes liveness probe |
| `/actuator/health/readiness` | GET | Kubernetes readiness probe |
| `/api/info` | GET | Environment, uptime, feature flags |
| `/api/health/deep` | GET | Memory usage, detailed health |
| `/api/items` | GET | List all items (DynamoDB) |
| `/api/items` | POST | Create item |
| `/api/items/{id}` | GET | Get item by ID |
| `/api/items/{id}` | PUT | Update item |
| `/api/items/{id}` | DELETE | Delete item |

## Getting Started

### Prerequisites

```bash
# Node.js (for CDK)
node --version   # >= 18.x

# AWS CDK CLI
npm install -g aws-cdk
cdk --version    # >= 2.x

# AWS CLI configured
aws sts get-caller-identity

# kubectl
kubectl version --client

# Docker
docker --version
```

### 1. Bootstrap CDK (One-Time)

```bash
cdk bootstrap aws://733508956784/us-east-1
```

### 2. Install Dependencies

```bash
cd atlas-platform-cdk
npm install
```

### 3. Deploy Pipeline

```bash
# First deploy (creates the pipeline which then manages itself)
cdk deploy PipelineStack
```

After this, every `git push` to main triggers the pipeline automatically.

### 4. Manual Deploy (for development)

```bash
# Deploy a specific environment stack directly
cdk deploy AtlasDev/InfraStack
cdk deploy AtlasStaging/InfraStack

# Deploy all
cdk deploy --all
```

### 5. Verify

```bash
aws eks update-kubeconfig --name atlas-platform-dev --region us-east-1
kubectl get pods -n atlas-platform
kubectl port-forward svc/atlas-platform 8080:80 -n atlas-platform

# Test endpoints
curl http://localhost:8080/api/info
curl http://localhost:8080/api/items
curl -X POST http://localhost:8080/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test-item", "description": "hello from atlas"}'
```

## Pipeline Stages

```
git push origin main
    │
    ▼
┌── 1. Source ────────────────────────────────────────────────────────┐
│   GitHub → CodeStar Connection                                       │
└──────────────────────────────────────────────────────┬───────────────┘
                                                       │
┌── 2. Build ──────────────────────────────────────────▼───────────────┐
│   CDK Synth → Maven build → Docker build (amd64) → Push to ECR       │
└──────────────────────────────────────────────────────┬───────────────┘
                                                       │
┌── 3. Deploy Dev ─────────────────────────────────────▼───────────────┐
│   CDK Deploy (infra) → kubectl apply → Smoke Tests ✅ → Auto-promote │
└──────────────────────────────────────────────────────┬───────────────┘
                                                       │
┌── 4. Deploy Staging ─────────────────────────────────▼───────────────┐
│   CDK Deploy → kubectl apply → Integration Tests ✅ → Auto-promote   │
└──────────────────────────────────────────────────────┬───────────────┘
                                                       │
┌── 5. Manual Approval ────────────────────────────────▼───────────────┐
│   ⛔ SNS notification sent → Human reviews → Clicks "Approve"        │
└──────────────────────────────────────────────────────┬───────────────┘
                                                       │
┌── 6. Deploy Prod ────────────────────────────────────▼───────────────┐
│   CDK Deploy → kubectl apply → Smoke Tests → CloudWatch Alarm Check   │
└──────────────────────────────────────────────────────────────────────┘
```

## Integration Test Strategy

### Smoke Tests (dev + prod)
- `GET /actuator/health` → 200 OK
- `GET /api/info` → correct environment name
- Pod count >= minReplicas
- No CrashLoopBackOff pods

### Integration Tests (staging only)
- Full CRUD lifecycle: Create → Read → Update → Delete item
- Error handling: 404 for missing item, 400 for invalid payload
- DynamoDB connectivity verification
- Load test: 100 virtual users, 60 seconds, p95 < 500ms
- HPA trigger validation under load

## Security Practices

- **No public IPs** on EKS nodes (private subnets only)
- **VPC Endpoint** for DynamoDB (no NAT cost, private traffic)
- **IRSA** for pod-level DynamoDB access (least privilege)
- **Non-root container** user in Dockerfile
- **Secrets Manager** for credentials (never hardcoded)
- **CodeBuild in VPC** with security group rules to EKS
- **Manual approval** before production deployment
- **Self-mutating pipeline** (infrastructure changes go through same gates)

## CDK Commands Reference

| Command | Purpose |
|---|---|
| `cdk bootstrap` | One-time account setup (creates CDKToolkit stack) |
| `cdk synth` | Generate CloudFormation templates |
| `cdk diff` | Preview changes (like `terraform plan`) |
| `cdk deploy` | Deploy stack (like `terraform apply`) |
| `cdk destroy` | Tear down stack (like `terraform destroy`) |
| `cdk list` | List all stacks |
| `npm test` | Run CDK unit tests |

## Cost Estimate (Monthly)

| Resource | Dev | Staging | Prod |
|---|---|---|---|
| EKS Control Plane | $73 | $73 | $73 |
| NAT Gateway | $32 | $32 | $96 (3x) |
| EC2 Nodes | ~$60 | ~$120 | ~$180 |
| DynamoDB (on-demand) | ~$1 | ~$5 | ~$20 |
| VPC Endpoint (DynamoDB) | $7 | $7 | $11 |
| ECR + S3 + CloudWatch | ~$10 | ~$10 | ~$15 |
| **Total** | **~$183** | **~$247** | **~$395** |

## Author

**Tonmoy Dhar** — DevOps Engineer 2, Amazon

## License

MIT
