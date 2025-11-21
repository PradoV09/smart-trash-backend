import {
  ConflictException,
  HttpException,
  Injectable,
  InternalServerErrorException,
  UnauthorizedException,
} from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import * as bcrypt from 'bcrypt';
import { Roles } from './entities/roles.entity';
import { LoginUserDto } from './dto/login-user.dto';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,

    @InjectRepository(Roles)
    private readonly rolesRepository: Repository<Roles>,

    private readonly jwtService: JwtService,
  ) {}

  async create(createUserDto: CreateUserDto) {
    try {
      const { user } = createUserDto;

      const passwordPlain = createUserDto.password;
      const saltRounds = 10;

      const passwordHash = await bcrypt.hash(passwordPlain, saltRounds);

      const existingUser = await this.userRepository.findOneBy({ user });

      if (existingUser) {
        throw new ConflictException('El usuario ya se encuentra registrado');
      }

      const role = await this.rolesRepository.findOneBy({
        name: 'admin',
      });

      if (!role) {
        throw new Error('El rol asignado no existe en la BD');
      }

      const newUser = this.userRepository.create({
        ...createUserDto,
        password: passwordHash,
        role: role,
      });

      const savedUser = await this.userRepository.save(newUser);

      return {
        msg: 'El usuario fue creado con éxito',
        userName: savedUser.user,
        userRol: savedUser.role.name,
      };
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      console.error(error);
      throw new InternalServerErrorException('Error al crear el usuario');
    }
  }

  async login(loginUserDto: LoginUserDto) {
    try {
      const user = await this.userRepository.findOneBy({
        user: loginUserDto.user,
      });

      if (!user) {
        throw new UnauthorizedException('Usuario no encontrado');
      }

      const isPasswordValid = await bcrypt.compare(
        loginUserDto.password,
        user.password,
      );

      if (!isPasswordValid) {
        throw new UnauthorizedException('Contraseña incorrecta');
      }

      const payload = { id: user.id };
      
      const accessToken = this.jwtService.sign(payload, {
        secret: process.env.JWT_SECRET,
        expiresIn: '15m', 
      });

      const refreshToken = this.jwtService.sign(payload, {
        secret: process.env.JWT_REFRESH_SECRET,
        expiresIn: '7d',
      });

      const hashedRefreshToken = await bcrypt.hash(refreshToken, 10);

      await this.userRepository.update(user.id, {
        refresh_token: hashedRefreshToken,
      });

      return {
        message: 'Has iniciado sesión',
        userName: user.user,
        access_token: accessToken,
      };
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      console.error(error);
      throw new InternalServerErrorException('Error al iniciar sesión');
    }
  }

  findOne(id: string) {
    return `This action returns a #${id} user`;
  }

  update(id: string, updateUserDto: UpdateUserDto) {
    return `This action updates a #${id} user`;
  }
}
