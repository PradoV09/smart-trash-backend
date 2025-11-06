import { Module } from '@nestjs/common';
import { AppService } from './app.service';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm'; // Integración de TypeORM con NestJS para manejar la conexión y entidades de la base de datos
import { AppController } from './app.controller'; // Acceso a las variavbles de entorno

@Module({
  imports: [
    ConfigModule.forRoot({
      // Se encargará de traernos los datos del archivo de entorno .env
      isGlobal: true, // hacer global el ConfigModule
      //Esto sirve para que no tengas que importar todo el rato el ConfigModule en otros módulos de Nest donde lo necesites usar.
      envFilePath:
        process.env.NODE_ENV === 'production'
          ? '.env.production'
          : '.env.development',
    }),
    TypeOrmModule.forRootAsync({
      useFactory: () => ({
        type: 'postgres', // Tipo de base de datos a usar: PostgreSQL
        host: process.env.DB_HOST, // Host donde se encuentra la base de datos (desde la variable de entorno)
        port: Number(process.env.DB_PORT), // Puerto de conexión a la base de datos (convertido a número)
        username: process.env.DB_USER, // Usuario para autenticarse en la base de datos
        password: process.env.DB_PASSWORD, // Contraseña del usuario de la base de datos
        database: process.env.DB_NAME, // Nombre de la base de datos a conectar
        entities: [__dirname + '/**/*.entity{.ts,.js}'], // Rutas de las entidades para TypeORM (archivos .ts o .js dentro del proyecto)

        // Sincroniza automáticamente las entidades con la base de datos
        // Se desactiva en producción para no perder datos
        synchronize: process.env.NODE_ENV !== 'production',
      }),
    }),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
