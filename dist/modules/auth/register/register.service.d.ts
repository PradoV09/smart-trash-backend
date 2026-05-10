import { CreateUserDto } from '@modules/users/dto/create-user.dto';
import { UsersService } from '@modules/users/users.service';
export declare class RegisterService {
    private readonly usersService;
    constructor(usersService: UsersService);
    register(dto: CreateUserDto): Promise<{
        message: string;
        id: string;
        username: string;
    }>;
}
