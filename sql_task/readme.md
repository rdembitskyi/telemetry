You can start db by calling

```bash
docker run --name pg-telemetry -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```
And then connect via

```bash
psql -h localhost -U postgres -d telemetry
```

Stop and remove the container with:

```bash
docker stop pg-telemetry && docker rm pg-telemetry
```