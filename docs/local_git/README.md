# Local Git & CI/CD (OpenClaw cluster)

Documentation for a **local Gitea + distributed Gitea Actions runners** stack that sits alongside the existing Smart Factory API, Redis collaboration, and OpenClaw workflows.

| Document | Purpose |
|----------|---------|
| [LOCAL_CICD_BLUEPRINT.md](./LOCAL_CICD_BLUEPRINT.md) | Architecture, GitHub→Gitea migration, backup, risks, roadmap |
| [BUILD_WORKFLOW.md](./BUILD_WORKFLOW.md) | End-to-end build workflow (git push → CI → artifacts → Smart Factory) |
| [DEVICE_DINOSAUR.md](./DEVICE_DINOSAUR.md) | Mac host: Gitea, DB, optional MinIO, runner |
| [DEVICE_VANGUARD.md](./DEVICE_VANGUARD.md) | Raspberry Pi (arm64): runner + orchestrator |
| [DEVICE_JARVIS.md](./DEVICE_JARVIS.md) | x86_64 Linux dev/build node |
| [DEVICE_WINDOWS.md](./DEVICE_WINDOWS.md) | Windows build/test node |
| [DEVICE_TESLA.md](./DEVICE_TESLA.md) | x86_64 render & automated test node |
| [DEVICE_NEWTON.md](./DEVICE_NEWTON.md) | Optional/offline compile node |

**Related Smart Factory docs**

- API & CI/CD hooks: [../REQUIREMENTS.md](../REQUIREMENTS.md) (pipelines, `POST /api/webhook/github`, `GET/PATCH /api/cicd/builds`)
- Redis streams: [../REDIS_COLLABORATION.md](../REDIS_COLLABORATION.md)
- High-level harness: [../HIGH_REQUIREMENTS.md](../HIGH_REQUIREMENTS.md)
