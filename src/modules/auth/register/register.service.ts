import { ConflictException, Injectable, InternalServerErrorException } from '@nestjs/common';
import { CreateUserDto } from 'src/modules/users/dto/create-user.dto';
import { UsersService } from 'src/modules/users/users.service';
const bcrypt = require('bcrypt');

@Injectable()
export class RegisterService {
    constructor(private readonly usersService: UsersService) { }

    async register(dto: CreateUserDto) {
        const user = await this.usersService.create(dto);

        return {
            message: "Usuario creado correctamente",
            id: user.id,
            username: user.nameuser,
        };
    }
}
