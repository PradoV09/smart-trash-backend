import { ApiProperty } from '@nestjs/swagger';
import { IsString, MinLength } from 'class-validator';

export class LoginUserDto {
  @ApiProperty({ description: 'El nombre del usuario', example: 'jose_dev', required: true })
  @IsString()
  @MinLength(1)
  nameuser: string;

  @ApiProperty({ description: 'La contraseña del usuario', example: '123456789', required: true })
  @IsString()
  @MinLength(6)
  password: string;
}