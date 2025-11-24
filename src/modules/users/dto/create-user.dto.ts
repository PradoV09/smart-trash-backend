import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, MinLength, Matches } from 'class-validator';

export class CreateUserDto {

    @ApiProperty({ description: 'El nombre del usuario', example: 'jose_dev', required: true })
    @IsNotEmpty()
    @Matches(/^[a-zA-Z0-9_]+$/, { message: 'El nombre de usuario solo puede contener letras, números y guiones bajos' })
    @MinLength(1)
    nameuser: string;

    @ApiProperty({ description: 'La contraseña del usuario', example: '123456789', required: true })
    @IsNotEmpty()
    @MinLength(8)
    password: string;
}
