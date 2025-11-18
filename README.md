# 🚛 Smart Trash Routes – Backend (NestJS)

> API del sistema web para gestionar y visualizar rutas de camiones de basura en Buenaventura 🌍  
> **Backend desarrollado completamente por: _Jose Luis Prado Valencia_**

---

## 🧠 Contexto del Problema

En Buenaventura no hay claridad sobre los horarios ni los recorridos de los camiones de basura. Esto genera:

- 🗑️ Acumulación de residuos  
- 😷 Malos olores  
- 🚯 Desorden en las calles  

El backend de este proyecto se encarga de manejar toda la lógica, datos y validaciones necesarias para soportar la solución.

---

## 🎯 Objetivo del Backend

Este servidor implementado en **NestJS** tiene como propósito:

- 🧍‍♂️ Gestionar **camiones y empleados (CRUD)**  
- 🚚 Manejar **rutas y posiciones geográficas**  
- 🛰️ Proveer endpoints para **simulación de recorridos en tiempo real**  
- 🔐 Administrar seguridad, validaciones y manejo de datos  
- 🗺️ Servir datos geoespaciales desde **PostgreSQL + PostGIS**  

---

## 🛠️ Tecnologías Utilizadas

| Área              | Herramientas                        |
| ----------------- | ----------------------------------- |
| **Backend**       | NestJS, TypeORM, pnpm               |
| **Base de Datos** | PostgreSQL + PostGIS                |
| **DevOps**        | GitHub Actions (CI/CD)              |
| **Metodología**   | GitHub Projects, Scrum              |

---

## 📦 Instalación y Ejecución del Backend

### 🔧 1. Clonar el repositorio

```bash
git clone https://github.com/PradoV09/smart-trash-routes-backend.git
cd smart-trash-routes-backend
````

### 📁 2. Instalar dependencias

```bash
npm install
```

### ⚙️ 3. Crear el archivo `.env`

Crea un `.env` basado en `.env.example`:

```
DB_HOST=
DB_PORT=
DB_USER=
DB_PASS=
DB_NAME=
JWT_SECRET=
```

### ▶️ 4. Ejecutar en modo desarrollo

```bash
npm run start:dev
```

* Backend: [http://localhost:8080](http://localhost:8080)

### 🏗️ 5. Compilar para producción

```bash
npm run build
```

---

## 📅 Metodología de Trabajo

El proyecto se desarrolló bajo **Scrum**, con entregas organizadas en GitHub Projects.

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

> **Backend creado completamente por:**
> **Jose Luis Prado Valencia** – Developer
> GitHub: [@PradoV09](https://github.com/PradoV09)

> **Frontend desarrollado por:**

| Nombre                      | Rol          | GitHub                                                       |
| --------------------------- | ------------ | ------------------------------------------------------------ |
| Jonatan Stewar Cuero Moreno | Scrum Master | [@JonatanCueroMoreno](https://github.com/JonatanCueroMoreno) |
| Heiner Jair Godoy Zamora    | Developer    | [@heiner-godoy](https://github.com/heiner-godoy)             |

---

## 🧪 CI/CD

Este backend utiliza **GitHub Actions** para automatizar:

1. ✅ Lint + Tests
2. 🏗️ Build del backend
3. 🚀 Deploy a entorno de staging o producción

---

## 🧑‍💻 Requisitos Previos

* **Node.js >= 18**
* **pnpm >= 8**
* **PostgreSQL** con **PostGIS** habilitado

---

## 📄 Licencia

**MIT License** – Proyecto académico de la **Universidad del Valle**.
Uso libre con fines educativos.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Abre un issue o pull request para mejoras o sugerencias.

---

**Desarrollado con 💚 por el equipo Smart Trash Routes – Universidad del Valle**
*Backend construido por Jose Luis Prado Valencia*