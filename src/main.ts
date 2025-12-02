import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { UsersSeederService } from './seeders/users-seeder/users-seeder.service';
import { RolesSeederService } from './seeders/roles-seeder/roles-seeder.service';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  app.enableCors({
    origin: 'http://localhost:4200',
    methods: 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
    allowedHeaders: 'Content-Type, Authorization'
  });

  const rolesSeeder = await app.get(RolesSeederService)
  await rolesSeeder.run()

  const userSeeder = await app.get(UsersSeederService)
  await userSeeder.run()

  const configervice = app.get(ConfigService);

  const options = new DocumentBuilder()
    .setTitle('smart-trash-backend')
    .setDescription(
      'API del backend de Smart Trash Routes para gestionar camiones, empleados y rutas en tiempo real',
    )
    .setVersion('2.0')
    .build();

  const document = SwaggerModule.createDocument(app, options);
  SwaggerModule.setup('doc', app, document);

  const PORT = configervice.get('PORT');
  app.setGlobalPrefix('api')

  await app.listen(PORT, '0.0.0.0');
  console.log('El servidor esta funcionando en el puerto: ', PORT);
}
bootstrap();

