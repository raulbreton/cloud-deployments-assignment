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
```

## Endpoints Principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/message` | Devuelve el mensaje de estado y la versión de la aplicación |
| `GET` | `/api/notes` | Obtiene el listado de notas almacenadas |
| `POST` | `/api/notes` | Crea una nueva nota (`{"text": "..."}`) |
| `DELETE` | `/api/notes/{id}` | Elimina una nota existente |
| `GET` | `/livez` | Sonda de actividad (*Liveness probe*) |
| `GET` | `/readyz` | Sonda de disponibilidad (*Readiness probe*) |
| `GET` | `/docs` | Documentación interactiva Swagger UI |

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
| :--- | :--- | :--- |
| `PORT` | `8080` | Puerto interno en el que escucha el contenedor |
| `APP_MESSAGE` | `Hello from the API` | Mensaje personalizado devuelto por `/api/message` |
| `APP_VERSION` | `dev` | Versión o hash de commit desplegado |
| `CORS_ORIGIN` | `http://localhost:5173` | URL del frontend autorizada para realizar peticiones |
| `DB_URL` | *(Requerida)* | Cadena de conexión a la base de datos |

---

## Ejecución Local

### 1. API con Docker
Desde la raíz del proyecto, compila y ejecuta el contenedor mapeando el puerto `8080`:

```bash
docker build -t api .
docker run --rm -p 8080:8080 api
```
* **Verificación:** Accede a `http://localhost:8080/docs` para probar los endpoints en Swagger.

### 2. Frontend Estático
Desde la raíz del proyecto, instala dependencias y compila los artefactos de distribución:

```bash
npm --prefix web ci
npm --prefix web run build
```
* El resultado se genera en `web/dist/` listo para ser servido o subido al almacenamiento estático.

---

## Despliegue en la Nube (Azure)

1. **Base de Datos Gestionada:** Aprovisionar el servicio de base de datos en Azure, configurar reglas de red y obtener la cadena de conexión.
2. **Registro de Contenedores (Docker Hub):**
   ```bash
   docker login
   docker build -t <usuario-dockerhub>/seminar-api:1.0 .
   docker push <usuario-dockerhub>/seminar-api:1.0
   ```
3. **API en Azure Container Apps:**
   * Crear la aplicación apuntando a la imagen `<usuario-dockerhub>/seminar-api:1.0` con *Ingress* habilitado en el puerto destino `8080`.
   * Configurar la cadena de conexión en **Secrets** y mapear `DB_URL` y `CORS_ORIGIN` como variables de entorno.
4. **Frontend en Azure Blob Storage:**
   * Habilitar *Static Website* en la cuenta de almacenamiento.
   * Actualizar `web/dist/config.js` con la URL pública HTTPS de Container Apps y subir el contenido:
   ```bash
   az storage blob upload-batch --account-name <storage_account_name> -s web/dist -d '$web' --overwrite
   ```

## Seguridad y Buenas Prácticas

* **Cero secretos en el código:** Ninguna contraseña, token o cadena de conexión se almacena en el repositorio; se gestionan exclusivamente mediante variables de entorno y secretos del proveedor cloud.
* **Higiene de Git:** Los archivos locales temporales (`venv/`, `__pycache__/`, `*.db`, `.env`) están excluidos mediante `.gitignore`.