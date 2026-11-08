# Cloud Deployments Assignment - FastAPI Note API

API desarrollada en FastAPI y containerizada con Docker para su despliegue en Azure Container Apps.

## Ejecución local con Docker
```bash
docker build -t api .
docker run --rm -p 8080:8080 api