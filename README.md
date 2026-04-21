ecs-project/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── data-model.md
│   └── test-scenarios.md
├── infra/
│   ├── postgres/
│   │   └── init.sql
│   └── kafka/
│       └── create-topics.sh
├── shared/
│   └── contracts/
│       ├── topics.py
│       └── events.py
├── services/
│   ├── ingestion/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   └── routes.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   └── database.py
│   │   │   ├── models/
│   │   │   │   └── energy.py
│   │   │   ├── schemas/
│   │   │   │   └── energy.py
│   │   │   ├── services/
│   │   │   │   ├── validation_service.py
│   │   │   │   └── ingestion_service.py
│   │   │   ├── producers/
│   │   │   │   └── kafka_producer.py
│   │   │   ├── repositories/
│   │   │   │   ├── prices_repo.py
│   │   │   │   └── forecasts_repo.py
│   │   │   └── utils/
│   │   │       └── time.py
│   │   └── tests/
│   │       ├── test_validation.py
│   │       └── test_api.py
│   ├── optimization/
│   │   └── .keep
│   └── intraday/
│       └── .keep
└── frontend/
    └── .keep


temp tree
