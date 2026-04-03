# 🚛 Smart Trash Routes – Backend (FastAPI)

![Version](https://img.shields.io/badge/version-2.0-blue)

> ⚠️ **Versión 2.0** – Reescritura completa del backend usando **FastAPI (Python)**.  
> La versión anterior desarrollada en **NestJS (Node.js)** está disponible en la rama `legacy-v1`.

> API del sistema web para gestionar y visualizar rutas de camiones de basura en Buenaventura 🌍  
> **Backend desarrollado por: _Jose Luis Prado Valencia y Heiner Jair Godoy Zamora_**

---

## 🧠 Contexto del Problema

En Buenaventura no hay claridad sobre los horarios ni los recorridos de los camiones de basura. Esto genera:

- 🗑️ Acumulación de residuos
- 😷 Malos olores
- 🚯 Desorden en las calles

El backend de este proyecto se encarga de manejar toda la lógica, datos y validaciones necesarias para soportar la solución.

---

## 🎯 Objetivo del Backend

Este servidor implementado en **FastAPI** tiene como propósito:

- 🧍‍♂️ Gestionar **camiones y empleados (CRUD)**
- 🚚 Manejar **rutas y posiciones geográficas**
- 🛰️ Proveer endpoints para **simulación de recorridos en tiempo real**
- 🔐 Administrar seguridad, validaciones y manejo de datos
- 🗺️ Servir datos geoespaciales desde **PostgreSQL + PostGIS**
- ⚡ Estar **optimizado con programación asíncrona (`async`/`await`)** para mejorar rendimiento y concurrencia
- 🌐 Consumir y extender la **API del profesor**: [https://apirecoleccion.gonzaloandreslucio.com/](https://apirecoleccion.gonzaloandreslucio.com/)
- 📖 Documentación de la API del profesor: [https://apirecoleccion.gonzaloandreslucio.com/api/documentation#/](https://apirecoleccion.gonzaloandreslucio.com/api/documentation#/)

---

## � Documentación de la API

Además de la documentación automática de FastAPI, este repositorio incluye una guía técnica detallada:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Guía funcional de la API:** [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)
- **Guía técnica interna para el equipo:** [`DEVELOPER_GUIDE.md`](./DEVELOPER_GUIDE.md)

### 📌 Formato de respuesta unificado

Todas las rutas devuelven el siguiente formato estándar:

- `success: true` (operaciones exitosas):

```json
{
  "success": true,
  "message": "Operación completada correctamente.",
  "data": { ... }
}
```

- `success: false` (errores):

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Recurso no encontrado.",
    "details": null,
    "path": "/ruta",
    "method": "GET",
    "timestamp": "2026-04-02T18:00:00+00:00"
  }
}
```

Esto facilita el consumo de la API desde clientes móviles y web, y reduce lógica extra en el frontend.

### 📌 Soporte de formulario en Swagger

Para los endpoints que reciben payloads (create/update), se implementó `as_form()` en los schemas:
- `XxxCreate.as_form()` y `XxxUpdate.as_form()`
- uso de `Form(...)` para requeridos y `Form(None)` para opcionales
- controladores con `Depends(XxxCreate.as_form)` o `Depends(XxxUpdate.as_form)`

De esta forma Swagger muestra campos separados y el servidor sigue aceptando JSON o form-data.

---

## �🛠️ Tecnologías Utilizadas

| Área                                | Herramientas                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Backend**                         | FastAPI, SQLAlchemy async, pip                                                                   |
| **Base de Datos**                   | PostgreSQL + PostGIS + `asyncpg`                                                                 |
| **DevOps**                          | GitHub Actions (CI/CD)                                                                           |
| **Metodología**                     | GitHub Projects, Scrum                                                                           |
| **Frontend web para administrador** | Angular (repo: [smart-trash-routes-web](https://github.com/PradoV09/smart-trash-routes.git))     |
| **Frontend mobile para ciudadano**  | Ionic (repo: [smart-trash-routes-mobile](https://github.com/PradoV09/smart-trash-routes-Mobile)) |

---

## 📦 Instalación y Ejecución del Backend

### 🔧 1. Clonar el repositorio

```bash
git clone https://github.com/PradoV09/smart-trash-routes-backend-fastapi.git
cd smart-trash-routes-backend
```

### 📁 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### ⚙️ 3. Crear el archivo `.env`

Crea un `.env` basado en `.env.example`:

```
DATABASE_URL=
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
```

### ▶️ 4. Ejecutar en modo desarrollo

```bash
uvicorn main:app --reload
```

- Backend: [http://localhost:8000](http://localhost:8000)

### 🏗️ 5. Compilar para producción

```bash
uvicorn main:app
```

---

## 🧪 Pruebas automáticas (pytest)

Se agregaron pruebas de integración en `tests/test_api.py` usando `httpx.AsyncClient(app=app)`.

Instala dependencias de test si no están:

```bash
pip install pytest pytest-asyncio httpx
```

Ejecuta:

```bash
pytest -q
```

Esto verifica:
- `GET /` → 200, `success: true`
- `POST /auth/login` con credenciales válidas
- `POST /auth/login` con payload inválido
- `GET /no-existe` → 404

---

## 🌐 Consumo de la API del Profesor

Este backend **consume y extiende** la API de tu profesor para obtener datos de:

- Vehículos y rutas
- Empleados y roles
- Estados de recolección de basura
- El identificador `id_ruta`, que es asignado por la **API externa** y no por este backend

Todos los endpoints están documentados aquí: [API del profesor](https://apirecoleccion.gonzaloandreslucio.com/api/documentation#/).

---

## 📅 Metodología de Trabajo

Desarrollo bajo **Scrum**, con entregas organizadas en GitHub Projects.

### 🧩 Entregables del backend por sprint

1. 🧱 Configuración inicial del servidor
2. 🗄️ Modelado de base de datos + entidades
3. 🔐 Módulos base (auth, usuarios, roles)
4. 🚚 CRUD de camiones y empleados
5. 🗺️ Rutas geoespaciales + PostGIS
6. 🛰️ Simulación de posiciones
7. 🧪 Validaciones, documentación y pruebas

---

## 👥 Equipo de Desarrollo

> **Backend:** Jose Luis Prado Valencia, Heiner Jair Godoy Zamora – Developers
> GitHub: [@PradoV09](https://github.com/PradoV09), [@heiner-godoy](https://github.com/heiner-godoy)

> **Frontend:** Angular (repo: [smart-trash-routes](https://github.com/PradoV09/smart-trash-routes.git))

---

## 🧪 CI/CD

Este backend utiliza **GitHub Actions** para automatizar:

1. ✅ Lint + Tests
2. 🏗️ Build del backend
3. 🚀 Deploy a entorno de staging o producción

---

## 🧑‍💻 Requisitos Previos

- **Python >= 3.8**
- **pip**
- **PostgreSQL** con **PostGIS** habilitado

---

## 📄 Licencia

**MIT License** – Proyecto académico de la **Universidad del Valle**.
Uso libre con fines educativos.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Abre un issue o pull request para mejoras o sugerencias.

---

**Desarrollado con 💚 en el contexto de un proyecto académico de la Universidad del Valle**

_Backend desarrollado por Heiner Jair Godoy Zamora._