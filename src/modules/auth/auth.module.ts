import { Module } from '@nestjs/common';
import { RegisterService } from './register/register.service';
import { LoginService } from './login/login.service';
import { LogoutService } from './logout/logout.service';
import { AuthController } from './auth.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from '../users/entities/user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User])],
  controllers: [AuthController],
  providers: [RegisterService, LoginService, LogoutService]
})
export class AuthModule { }
