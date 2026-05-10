import { User } from '@modules/users/entities/user.entity';
import { UsersService } from '@modules/users/users.service';
import { Repository } from 'typeorm';
export declare class UsersSeederService {
    private readonly userRepository;
    private readonly usersService;
    constructor(userRepository: Repository<User>, usersService: UsersService);
    run(): Promise<void>;
}
