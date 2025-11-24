import { Injectable, UnauthorizedException } from '@nestjs/common';
import { LoginUserDto } from 'src/modules/users/dto/login-user.dto';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from 'src/modules/users/users.service';

@Injectable()
export class LoginService {
  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
  ) {}

  async login(dto: LoginUserDto) {
    const name = dto.nameuser.toLowerCase().trim();
    const user = await this.usersService.findByName(name);

    if (!user) throw new UnauthorizedException("Credenciales incorrectas");

    const isMatch = await bcrypt.compare(dto.password, user.password);
    if (!isMatch) throw new UnauthorizedException("Credenciales incorrectas");

    const payload = { sub: user.id, username: user.nameuser };
    const accessToken = this.jwtService.sign(payload);

    return { accessToken, username: user.nameuser };
  }
}
