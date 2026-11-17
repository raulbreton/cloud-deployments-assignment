# Cloud Deployments Assignment — 3-Service Notes App

Aplicación web de notas compuesta por tres servicios desplegados en la nube: un frontend estático, una API REST contenedorizada en Python (FastAPI) y una base de datos gestionada.

## Arquitectura

* **Frontend (`web/`):** Interfaz web desarrollada en React + Vite, compilada como sitio estático y alojada en **Azure Blob Storage** (`$web`).
* **API (`main.py`):** Servicio REST CRUD desarrollado en **FastAPI (Python)**, empaquetado con Docker y desplegado en **Azure Container Apps**.
* **Base de Datos:** Recurso gestionado en la nube (PostgreSQL / Cosmos DB / Redis) conectado mediante variables de entorno y secretos de plataforma (SQLite local para pruebas).

## Estructura del Proyecto

```text
cloud-deployments-assignment/
├── web/                 # Frontend en React + Vite
├── main.py              # Código fuente de la API en FastAPI
├── Dockerfile           # Definición de imagen Docker optimizada para la API
├── requirements.txt     # Dependencias de Python
├── .gitignore           # Exclusión de entornos virtuales, caché y bases de datos locales
└── README.md            # Documentación del proyecto