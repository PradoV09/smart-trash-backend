import { Module } from '@nestjs/common';
import { AppService } from './app.service';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller'; // Acceso a las variavbles de entorno

@Module({
  imports: [ConfigModule.forRoot({  // Se encargará de traernos los datos del archivo de entorno .env
      isGlobal: true, // hacer global el ConfigModule
                      //Esto sirve para que no tengas que importar todo el rato el ConfigModule en otros módulos de Nest donde lo necesites usar.
      })],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
