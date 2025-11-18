import { ConflictException, Injectable } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import * as bcrypt from 'bcrypt';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}
  async create(createUserDto: CreateUserDto) {
    try {
      const { user } = createUserDto;

      const passwordPlain = createUserDto.password;

      const saltRounds = 10;

      const passwordHash = await await bcrypt.hash(passwordPlain, saltRounds);

      const existingUser = await this.userRepository.findOneBy({ user });

      if (existingUser) {
        throw new ConflictException('El usuario ya se encuentra registrado');
      }
      
      const newUser = this.userRepository.create({
        ...createUserDto,
        password: passwordHash,
      });

      const saveUser = this.userRepository.save(newUser);

      return {
        msg: 'El usuario fue creado con exito',
        user: newUser,
      };
    } catch (error) {
      throw new ConflictException(
        'El usuario ya se encuentra registrado',
        error,
      );
    }
  }

  findOne(id: number) {
    return `This action returns a #${id} user`;
  }

  update(id: number, updateUserDto: UpdateUserDto) {
    return `This action updates a #${id} user`;
  }
}
