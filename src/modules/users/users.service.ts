import { ConflictException, Injectable } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { User } from './entities/user.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { Role } from '@entities/roles.entity';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,

    @InjectRepository(Role)
    private readonly roleRepository: Repository<Role>
  ) { }

  async create(dto: CreateUserDto) {
    const nameuser = dto.nameuser.toLowerCase().trim();

    const exists = await this.userRepository.findOneBy({ nameuser });
    if (exists) throw new ConflictException("Ese usuario ya existe.");

    const passwordHash = await bcrypt.hash(dto.password, 10);

    const defaultRole = await this.roleRepository.findOne({
      where: { nameRol: 'ADMIN' }
    });

    if (!defaultRole) {
      throw new ConflictException("No existe el rol USER en la BD.");
    }

    const user = this.userRepository.create({
      ...dto,
      nameuser,
      password: passwordHash,
      role: defaultRole,
    });

    return this.userRepository.save(user);
  }

  async findByName(nameuser: string) {
    return this.userRepository
      .createQueryBuilder('user')
      .leftJoinAndSelect('user.role', 'role')
      .addSelect('user.password')
      .where('user.nameuser = :name', { name: nameuser })
      .getOne();
  }

  async findById(id: string) {
    return this.userRepository.findOneBy({ id });
  }

  async updateRefreshToken(id: string, refreshToken: string | null) {
    await this.userRepository.update(id, { refreshToken });
  }
}

