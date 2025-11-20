import { Module } from '@nestjs/common';
import { UsersSeederService } from './users-seeder.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from 'src/modules/users/entities/user.entity';
import { UsersModule } from 'src/modules/users/users.module';

@Module({
  imports: [TypeOrmModule.forFeature([User]), UsersModule],
  providers: [UsersSeederService]
})
export class UsersSeederModule {}
