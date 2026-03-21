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
- 🌐 Consumir y extender la **API del profesor**: [https://apirecoleccion.gonzaloandreslucio.com/](https://apirecoleccion.gonzaloandreslucio.com/)
- 📖 Documentación de la API del profesor: [https://apirecoleccion.gonzaloandreslucio.com/api/documentation#/](https://apirecoleccion.gonzaloandreslucio.com/api/documentation#/)

---

## 🛠️ Tecnologías Utilizadas

| Área                                | Herramientas                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Backend**                         | FastAPI, SQLAlchemy, pip                                                                         |
| **Base de Datos**                   | PostgreSQL + PostGIS                                                                             |
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

## 🌐 Consumo de la API del Profesor

Este backend **consume y extiende** la API de tu profesor para obtener datos de:

- Vehículos y rutas
- Empleados y roles
- Estados de recolección de basura

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

**Desarrollado con 💚 por el equipo Smart Trash Routes – Universidad del Valle**

_Backend construido por Jose Luis Prado Valencia y Heiner Jair Godoy Zamora_