<p align="center">
  <a href="https://nestjs.com/" target="blank">
    <img src="https://nestjs.com/img/logo-small.svg" width="120" alt="Nest Logo" />
  </a>
</p>

# Smart Trash Backend ♻️

<p align="center">
  API RESTful desarrollada con 
  <a href="http://nestjs.com/" target="_blank">NestJS</a> y 
  <a href="https://www.mysql.com/" target="_blank">MySQL</a> para el sistema de rutas inteligentes de recolección de basuras.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/NestJS-v10-red" alt="NestJS Version" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-blue" alt="TypeScript" />
  <img src="https://img.shields.io/badge/MySQL-8.0-orange" alt="MySQL" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
</p>

---

## 📘 Descripción del Proyecto

**Smart Trash Backend** es la capa de servicio central para el sistema de gestión de rutas inteligentes de recolección de basuras.

El proyecto está construido sobre **NestJS** (un *framework* progresivo de Node.js), utiliza **TypeORM** para la gestión de la base de datos **MySQL**, y cuenta con documentación de *endpoints* generada automáticamente mediante **Swagger**.

> **⚠️ Estado Actual:** El proyecto se encuentra en su **fase inicial**, preparando la estructura base sin módulos de negocio definidos.

---

## 🧰 Tecnologías Clave

Este proyecto utiliza las siguientes tecnologías:

* ⚙️ **NestJS** – *Framework* progresivo para la construcción de aplicaciones del lado del servidor.
* 📘 **TypeScript** – Lenguaje principal, que proporciona tipado estático.
* 🗄️ **MySQL** – Base de datos relacional.
* 🧩 **Swagger** – Para la documentación automática y visualización de la API.
* 🔐 **Dotenv** – Gestión de variables de entorno para configuración.

---

## 🚀 Instalación y Configuración

Sigue estos pasos para levantar el proyecto en tu entorno local.

### 1️⃣ Clonar el Repositorio

```bash
git clone [https://github.com/PradoV09/smart-trash-backend.git](https://github.com/PradoV09/smart-trash-backend.git)
cd smart-trash-backend
````

### 2️⃣ Instalar Dependencias

Se recomienda el uso de `pnpm` por su eficiencia:

```bash
pnpm install
# También puedes usar npm install o yarn install
```

### 3️⃣ Configurar Variables de Entorno

Crea un archivo llamado `.env.development` en la raíz del proyecto y añade la siguiente estructura con tus credenciales:

```bash
# Puerto del servidor
PORT=3000

# Configuración de la base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=tu_password
DB_NAME=smart_trash_db
```

-----

## 🧑‍💻 Scripts Disponibles

Ejecuta los siguientes comandos desde la raíz del proyecto:

| Comando | Descripción |
| :--- | :--- |
| `pnpm run start:dev` | Inicia el servidor en **modo desarrollo** con *hot reload*. |
| `pnpm run start:prod` | Inicia la aplicación compilada en **modo producción**. |
| `pnpm run build` | Compila el proyecto a JavaScript en el directorio `dist`. |

-----

## 🧭 Documentación de la API (Swagger)

Una vez que el servidor está en ejecución (por ejemplo, con `pnpm run start:dev`), la documentación de la API se genera automáticamente:

  * **URL de Acceso:** `http://localhost:3000/api/docs`

Swagger muestra todas las rutas registradas, DTOs y esquemas de datos.

-----

## 🧱 Estructura del Proyecto

La estructura inicial es la siguiente:

```
src/
│
├── main.ts              # Punto de entrada de la aplicación
├── app.module.ts        # Módulo raíz de la aplicación
└── config/              # Configuración general y de conexión a la base de datos
```

> 📦 En futuras versiones, los módulos de negocio (users, auth, routes, etc.) se agregarán bajo `src/modules/`.

-----

## 🧩 Próximas Implementaciones

Se planea añadir la siguiente funcionalidad:

  * **Módulo de Autenticación** (JWT).
  * **Módulo de Usuarios**.
  * **Módulo de Rutas** de recolección (lógica inteligente).
  * **Integración** con sensores o IoT.
  * Implementación de **Pruebas** unitarias y de integración.
  * **Deploy** con Docker o PM2.

-----

## 🌐 Despliegue a Producción

Para desplegar la aplicación en un entorno de producción:

1.  Compila la aplicación: `pnpm run build`
2.  Inicia la aplicación compilada: `pnpm run start:prod`

> **Recomendación:** Se sugiere usar herramientas como **PM2**, **Docker**, o servicios de *hosting* como **Railway**, **Render**, o **AWS** para asegurar que el servicio se mantenga activo y sea escalable.

-----

## 📖 Recursos Útiles

  * [NestJS Docs](https://docs.nestjs.com/)
  * [Swagger Docs](https://swagger.io/docs/)
  * [MySQL Docs](https://dev.mysql.com/doc/)
  * [TypeScript Docs](https://www.typescriptlang.org/docs/)

-----

## 👨‍💻 Autor y Licencia

### Autor

**Jose Luis Prado**
*Estudiante de Tecnología en Desarrollo de Software – Universidad del Valle*

  * 🔗 [GitHub del Autor](https://www.google.com/search?q=https://github.com/PradoV09)

### Licencia
  * Este proyecto está bajo la **Licencia MIT**.