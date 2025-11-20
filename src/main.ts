import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { RolesService } from './seeders/roles/roles.service';
import { UsersSeederService } from './seeders/users-seeder/users-seeder.service';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.setGlobalPrefix('api');

  // Swagger
  const configService = app.get(ConfigService);
  const options = new DocumentBuilder()
    .setTitle('smart-trash-backend')
    .setDescription(
      'API del backend de Smart Trash Routes para gestionar camiones, empleados y rutas en tiempo real',
    )
    .setVersion('2.0')
    .build();
  const document = SwaggerModule.createDocument(app, options);
  SwaggerModule.setup('doc', app, document);

  await app.init();

  const seedersRoles = app.get(RolesService);
  await seedersRoles.Run();

  const seedersUsers = app.get(UsersSeederService);
  await seedersUsers.Run();

  const PORT = configService.get('PORT');

  await app.listen(PORT);
  console.log('El servidor está funcionando en el puerto:', PORT);
}

bootstrap();
