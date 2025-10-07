import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ConfigService } from '@nestjs/config';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const configervice = app.get(ConfigService)
  const PORT = configervice.get('PORT')
  await app.listen(PORT ?? 3000);
  console.log(`Servidor corriendo en el puerto: ${PORT ?? 3000}`);
}
bootstrap();