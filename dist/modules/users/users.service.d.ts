import { CreateUserDto } from './dto/create-user.dto';
import { User } from './entities/user.entity';
import { Repository } from 'typeorm';
import { Role } from '@entities/roles.entity';
export declare class UsersService {
    private readonly userRepository;
    private readonly roleRepository;
    constructor(userRepository: Repository<User>, roleRepository: Repository<Role>);
    create(dto: CreateUserDto): Promise<User>;
    findByName(nameuser: string): Promise<User | null>;
    findById(id: string): Promise<User | null>;
    updateRefreshToken(id: string, refreshToken: string | null): Promise<void>;
}
