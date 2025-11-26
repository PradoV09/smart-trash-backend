import { Injectable, UnauthorizedException } from '@nestjs/common';
import { LoginUserDto } from '@modules/users/dto/login-user.dto';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UsersService } from '@modules/users/users.service';

@Injectable()
export class LoginService {
  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
  ) { }

  async login(dto: LoginUserDto) {
    const name = dto.nameuser.toLowerCase().trim();
    const user = await this.usersService.findByName(name);

    if (!user) throw new UnauthorizedException("Credenciales incorrectas");

    const isMatch = await bcrypt.compare(dto.password, user.password);
    if (!isMatch) throw new UnauthorizedException("Credenciales incorrectas");

    const payload = { sub: user.id, username: user.nameuser, userrol: user.role.nameRol };
    const accessToken = this.jwtService.sign(payload, {
      expiresIn: '15m',
    });

    const refreshToken = this.jwtService.sign(payload, {
      expiresIn: '7d',
    });

    const hashed = await bcrypt.hash(refreshToken, 10);
    await this.usersService.updateRefreshToken(user.id, hashed);

    return {
      accessToken,
      refreshToken,
      username: user.nameuser,
      userrol: user.role.nameRol
    };
  }

}
