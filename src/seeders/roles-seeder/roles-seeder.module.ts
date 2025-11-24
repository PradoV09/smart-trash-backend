import { Module } from '@nestjs/common';
import { RolesSeederService } from './roles-seeder.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Role } from 'src/entities/roles.entity';
import { UsersModule } from 'src/modules/users/users.module';

@Module({
  imports: [TypeOrmModule.forFeature([Role]), UsersModule],
  providers: [RolesSeederService]
})
export class RolesSeederModule { }
