import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.setGlobalPrefix('api');
  const configervice = app.get(ConfigService);
  const options = new DocumentBuilder()
    .setTitle('smart-trash-backend')
    .setDescription(
      `
Smart Trash Backend — Documentación Oficial

Sistema web para rastrear camiones de basura en Buenaventura. 
Permite a los ciudadanos visualizar rutas y horarios en un mapa interactivo, con simulación casi en tiempo real.
Incluye frontend en Angular, API backend en NestJS, y base de datos PostgreSQL con PostGIS para manejo de geodatos.
El proyecto sigue prácticas DevOps como CI/CD, pruebas automatizadas y despliegues eficientes.
`,
    )
    .setVersion('1.0')
    .build();
  const document = SwaggerModule.createDocument(app, options);
  SwaggerModule.setup('doc', app, document);
  const PORT = configervice.get('PORT');
  await app.listen(PORT ?? 3000);
  console.log(`Servidor corriendo en el puerto: ${PORT ?? 3000}`);
}
bootstrap();
