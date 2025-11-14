import { Module } from '@nestjs/common';
import { AppService } from './app.service';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm'; // Integración de TypeORM con NestJS para manejar la conexión y entidades de la base de datos
import { AppController } from './app.controller'; // Acceso a las variavbles de entorno
import { AuthModule } from './modules/auth/auth.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true, 
      envFilePath:
        process.env.NODE_ENV === 'production'
          ? '.env.production'
          : '.env.development',
    }),
    TypeOrmModule.forRootAsync({
      useFactory: () => ({
        type: 'postgres', 
        host: process.env.DB_HOST, 
        port: Number(process.env.DB_PORT), 
        username: process.env.DB_USER, 
        password: process.env.DB_PASSWORD, 
        database: process.env.DB_NAME, 
        entities: [__dirname + '/**/*.entity{.ts,.js}'], 
        synchronize: process.env.NODE_ENV !== 'production',
      }),
    }),
    AuthModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
