import { Roles } from '@common/decorators/roles.decorator';
import { JwtAuthGuard } from '@guards/jwt/jwt.guard';
import { RolesGuard } from '@guards/roles/roles.guard';
import { Body, Controller, Get, Param, Post, UseGuards } from '@nestjs/common';
import {
    ApiTags,
    ApiOperation,
    ApiResponse,
    ApiBearerAuth,
    ApiBody,
} from '@nestjs/swagger';
import { RutasService } from './rutas.service';

@Controller('rutas')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('ADMIN')
@ApiTags('Rutas')
export class RutasController {
    constructor(private readonly rutasService: RutasService) { }

    @Get('all')
    @ApiOperation({ summary: 'Obtener todas las rutas' })
    @ApiResponse({
        status: 200,
        description: 'Listado completo de rutas.',
        schema: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    id: { type: 'string', example: '1d23fa0c-7780-4de1-9f90-cc8e5a19e9be' },
                    nombre_ruta: { type: 'string', example: 'Ruta Puerto – 3' },
                    calles_ids: {
                        type: 'array',
                        items: { type: 'string', format: 'uuid' },
                        example: [
                            '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                            'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                        ]
                    }
                }
            }
        }
    })
    getAll() {
        return this.rutasService.getAll();
    }

    @Post('register')
    @ApiOperation({ summary: 'Registrar una nueva ruta' })
    @ApiResponse({
        status: 201,
        description: 'Ruta creada correctamente.',
    })
    @ApiResponse({
        status: 400,
        description: 'Datos inválidos.',
    })
    @ApiBody({
        schema: {
            type: 'object',
            properties: {
                nombre_ruta: {
                    type: 'string',
                    example: 'Ruta Puerto – 3',
                },
                calles_ids: {
                    type: 'array',
                    items: { type: 'string', format: 'uuid' },
                    example: [
                        '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                        'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                    ]
                }
            },
            required: ['nombre_ruta', 'calles_ids']
        }
    })
    create(@Body() body: any) {
        return this.rutasService.create(body);
    }

    @Get(':id')
    @ApiOperation({ summary: 'Obtener una ruta por ID' })
    @ApiResponse({
        status: 200,
        description: 'Ruta encontrada.',
        schema: {
            type: 'object',
            properties: {
                id: { type: 'string', example: '1d23fa0c-7780-4de1-9f90-cc8e5a19e9be' },
                nombre_ruta: { type: 'string', example: 'Ruta Puerto – 3' },
                calles_ids: {
                    type: 'array',
                    items: { type: 'string', format: 'uuid' },
                    example: [
                        '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                        'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                    ]
                }
            }
        }
    })
    @ApiResponse({ status: 404, description: 'Ruta no encontrada.' })
    findOneBy(@Param('id') id: string) {
        return this.rutasService.finOneBy(id);
    }
}
