import { Module } from '@nestjs/common';
import { VehiculosService } from './vehiculos.service';
import { VehiculosController } from './vehiculos.controller';
import { AuthModule } from '../auth/auth.module';

@Module({
    imports: [AuthModule],
    controllers: [VehiculosController],
    providers: [VehiculosService],
    exports: [VehiculosService]
})
export class VehiculosModule { }
