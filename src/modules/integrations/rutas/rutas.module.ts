import { Module } from '@nestjs/common';
import { RutasController } from './rutas.controller';
import { RutasService } from './rutas.service';
import { AuthModule } from '@modules/auth/auth.module';

@Module({
  imports: [AuthModule],
  controllers: [RutasController],
  providers: [RutasService],
  exports: [RutasService]
})
export class RutasModule {}
