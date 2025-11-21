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
        user: savedUser,
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

      return {
        message: 'Has iniciado sesión',
        user,
        access_token: this.jwtService.sign({ id: user.id }),
      };
    } catch (error) {
      throw new InternalServerErrorException('Error al iniciar sesión');
    }
  }

  findOne(id: number) {
    return `This action returns a #${id} user`;
  }

  update(id: number, updateUserDto: UpdateUserDto) {
    return `This action updates a #${id} user`;
  }
}
