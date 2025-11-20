import {
  ConflictException,
  HttpException,
  Injectable,
  InternalServerErrorException,
} from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import * as bcrypt from 'bcrypt';
import { Roles } from './entities/roles.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,

    @InjectRepository(Roles)
    private readonly rolesRepository: Repository<Roles>,
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

  findOne(id: number) {
    return `This action returns a #${id} user`;
  }

  update(id: number, updateUserDto: UpdateUserDto) {
    return `This action updates a #${id} user`;
  }
}
