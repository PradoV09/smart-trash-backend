import { Controller, Get } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { VehiculosService } from './vehiculos.service';

@Controller('vehiculos')
@ApiTags('vehiculos')
export class VehiculosController {
    constructor(
        private readonly vehiculosService: VehiculosService
    ){}

    @Get('all')
    getAll(){
        return this.vehiculosService.getAll()
    }
}
