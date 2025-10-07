import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configervice = app.get(ConfigService) // Obtiene una instancia del servicio de configuración de NestJS
  const PORT = configervice.get('PORT') // Obtiene el valor de la variable de entorno 'PORT' desde el .env
  await app.listen(PORT ?? 3000); // Inicia la aplicación en el puerto especificado o usa 3000 por defecto si no existe en el .env
  console.log(`Servidor corriendo en el puerto: ${PORT ?? 3000}`);
}
bootstrap();