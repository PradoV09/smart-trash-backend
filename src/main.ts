import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ConfigService } from '@nestjs/config';
import { RolesService } from './seeders/roles/roles.service';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const seedService = app.get(RolesService);
  await seedService.Run();
  await app.close();
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
  app.setGlobalPrefix('api');
  await app.listen(PORT);
  console.log('El servidor esta funcionando en el puerto: ', PORT);
}
bootstrap();
