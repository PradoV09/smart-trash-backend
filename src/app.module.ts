import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './modules/auth/auth.module';
import { UsersModule } from './modules/users/users.module';
import { RolesSeederModule } from './seeders/roles-seeder/roles-seeder.module';
import { UsersSeederModule } from './seeders/users-seeder/users-seeder.module';
import { VehiculosService } from './modules/vehiculos/vehiculos.service';
import { VehiculosController } from './modules/vehiculos/vehiculos.controller';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRoot({
      type: 'postgres',
      host: process.env.DB_HOST,
      port: Number(process.env.DB_PORT), 
      username: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      entities: [__dirname + '/**/*.entity{.ts,.js}'],
      synchronize: process.env.NODE_ENV !== 'production',
    }),
    AuthModule,
    UsersModule,
    RolesSeederModule,
    UsersSeederModule,
  ],
  controllers: [VehiculosController],
  providers: [VehiculosService],
})
export class AppModule {}
