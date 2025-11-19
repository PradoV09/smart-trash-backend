import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Roles } from 'src/modules/users/entities/roles.entity';
import { Repository } from 'typeorm';

@Injectable()
export class RolesService {
  constructor(
    @InjectRepository(Roles)
    private readonly rolesRepository: Repository<Roles>,
  ) {}

  async Run() {
    // Borrar roles existentes
    await this.rolesRepository.query('TRUNCATE TABLE "roles" CASCADE;');

    // Insertar nuevos roles
    const roles = [
      { name: 'admin', description: 'Acceso total al sistema' },
      { name: 'usuario', description: 'Acceso básico a las funciones' },
      { name: 'conductor', description: 'Gestión de rutas y recolecciones' },
    ];

    await this.rolesRepository.save(roles)
  }
}
