import { ConflictException, Injectable, InternalServerErrorException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { CreateUserDto } from 'src/modules/users/dto/create-user.dto';
import { User } from 'src/modules/users/entities/user.entity';
import { Repository } from 'typeorm';
const bcrypt = require('bcrypt');

@Injectable()
export class RegisterService {
    constructor(
        @InjectRepository(User)
        private readonly userRepository: Repository<User>
    ) { }
    async register(createUserDto: CreateUserDto) {
        try {
            const { nameuser, password } = createUserDto;

            const nameuserNormalized = nameuser.toLowerCase().trim();

            const existingUser = await this.userRepository.findOneBy({ nameuser: nameuserNormalized });

            if (existingUser) {
                throw new ConflictException('No se pudo crear el usuario');
            }

            const saltRounds = 10;
            const passwordHash = await bcrypt.hash(password, saltRounds);

            const newUser = this.userRepository.create({
                ...createUserDto,
                nameuser: nameuserNormalized,
                password: passwordHash,
            });

            const userSave = await this.userRepository.save(newUser);

            return {
                message: '¡Tu usuario ha sido creado correctamente!',
                id: userSave.id,
                username: userSave.nameuser,
            };
        } catch (error) {
            throw new InternalServerErrorException('Error interno al registrar usuario');
        }
    }
}
