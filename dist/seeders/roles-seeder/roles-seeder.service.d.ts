import { Role } from '@entities/roles.entity';
import { Repository } from 'typeorm';
export declare class RolesSeederService {
    private readonly rolesRepository;
    constructor(rolesRepository: Repository<Role>);
    run(): Promise<void>;
}
