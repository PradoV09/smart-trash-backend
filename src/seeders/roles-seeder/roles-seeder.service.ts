import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Role } from 'src/entities/roles.entity';
import { Repository } from 'typeorm';


@Injectable()
export class RolesSeederService {
    constructor(
        @InjectRepository(Role)
        private readonly rolesRepository: Repository<Role>
    ) { }
    async run() {
        await this.rolesRepository.query('TRUNCATE TABLE "roles" CASCADE');

        const roles = [
            { nameRol: 'ADMIN', description: 'Control total del sistema. Puede crear, editar y borrar usuarios, roles y configuraciones.' },
            { nameRol: 'USER', description: 'Usuario estándar con acceso a las funciones principales de la plataforma.' },
            { nameRol: 'DRIVER', description: 'Encargado de realizar rutas, reportar estados y manejar operaciones de transporte.' }
        ];
        await this.rolesRepository.save(roles)
    }
}
