# Services (dev)

Requirements:
 - docker, docker-compose
 - .env file (see template in repo root)

To run locally:
  docker-compose up --build

Visit http://localhost:8000/ for dashboard.
Prometheus metrics: http://localhost:8000/metrics
Redis channel: market:ticks
