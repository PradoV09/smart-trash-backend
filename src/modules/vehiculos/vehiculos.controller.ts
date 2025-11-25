import { Body, Controller, Delete, Get, Param, Post, Put, UseGuards } from '@nestjs/common';
import { ApiBody, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { VehiculosService } from './vehiculos.service';
import { JwtAuthGuard } from 'src/guard/jwt/jwt.guard';
import { RolesGuard } from 'src/guard/roles/roles.guard';
import { Roles } from 'src/common/decorators/roles.decorator';

@Controller('vehiculos')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('ADMIN')
@ApiTags('Vehiculos')
export class VehiculosController {
    constructor(
        private readonly vehiculosService: VehiculosService
    ) { }

    @Get('all')
    @ApiOperation({ summary: 'Obtener todos los vehículos' })
    @ApiResponse({
        status: 200,
        description: 'Lista de vehículos obtenida correctamente.'
    })
    @ApiResponse({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    })
    @ApiResponse({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    })
    getAll() {
        return this.vehiculosService.getAll()
    }

    @Post('register')
    @ApiOperation({ summary: 'Registrar un nuevo vehículo' })
    @ApiBody({
        description: 'Datos enviados desde Postman (sin perfil_id)',
        schema: {
            example: {
                placa: 'XYZ-123',
                marca: 'Ford Fiesta',
                modelo: '2022'
            }
        }
    })
    @ApiResponse({
        status: 201,
        description: 'Vehículo registrado exitosamente.'
    })
    @ApiResponse({
        status: 400,
        description: 'Error en los datos enviados.'
    })
    @ApiResponse({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    })
    @ApiResponse({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    })
    create(@Body() body: any) {
        return this.vehiculosService.create(body);
    }

    @Get(':id')
    @ApiOperation({ summary: 'Obtener un vehículo por ID' })
    @ApiResponse({
        status: 200,
        description: 'Vehículo encontrado correctamente.'
    })
    @ApiResponse({
        status: 404,
        description: 'Vehículo no encontrado.'
    })
    @ApiResponse({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    })
    @ApiResponse({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    })
    findOne(@Param('id') id: string) {
        return this.vehiculosService.findOne(id)
    }

    @Put(':id')
    @ApiOperation({ summary: 'Actualizar un vehículo existente' })
    @ApiBody({
        description: 'Datos a actualizar',
        schema: {
            example: {
                placa: 'XYZ-987',
                marca: 'Nissan Versa',
                modelo: '2023'
            }
        }
    })
    @ApiResponse({
        status: 200,
        description: 'Vehículo actualizado exitosamente.'
    })
    @ApiResponse({
        status: 400,
        description: 'Datos inválidos enviados.'
    })
    @ApiResponse({
        status: 404,
        description: 'Vehículo no encontrado.'
    })
    @ApiResponse({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    })
    @ApiResponse({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    })
    update(@Param('id') id: string, @Body() body: any) {
        return this.vehiculosService.update(id, body)
    }

    @Delete(':id')
    @ApiOperation({ summary: 'Eliminar un vehículo por ID' })
    @ApiResponse({
        status: 200,
        description: 'Vehículo eliminado exitosamente.'
    })
    @ApiResponse({
        status: 404,
        description: 'Vehículo no encontrado.'
    })
    @ApiResponse({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    })
    @ApiResponse({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    })
    remove(@Param('id') id: string) {
        return this.vehiculosService.remove(id)
    }
}
