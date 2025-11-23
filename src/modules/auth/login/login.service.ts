import { Injectable, UnauthorizedException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { LoginUserDto } from 'src/modules/users/dto/login-user.dto';
import { User } from 'src/modules/users/entities/user.entity';
import { Repository } from 'typeorm';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt'; // usar import en vez de require

@Injectable()
export class LoginService {
    constructor(
        @InjectRepository(User)
        private readonly userRepository: Repository<User>,
        private readonly jwtService: JwtService,
    ) { }

    async login(loginUserDto: LoginUserDto) {
        const { nameuser, password } = loginUserDto;

        // Buscar usuario
        const user = await this.userRepository
            .createQueryBuilder('user')
            .addSelect('user.password')
            .where('user.nameuser = :nameuser', { nameuser: nameuser.toLowerCase().trim() })
            .getOne();

        if (!user) {
            throw new UnauthorizedException('Credenciales incorrectas');
        }

        // Comparar contraseña
        const isMatch = await bcrypt.compare(password, user.password);

        if (!isMatch) {
            throw new UnauthorizedException('Credenciales incorrectas');
        }

        // Crear JWT
        const payload = { sub: user.id, username: user.nameuser };
        const accessToken = this.jwtService.sign(payload);

        return { accessToken, username: user.nameuser };
    }
}
