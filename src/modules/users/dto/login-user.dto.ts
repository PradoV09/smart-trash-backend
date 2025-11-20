import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, MinLength, IsString } from 'class-validator';

export class LoginUserDto {
  @ApiProperty({
    description: 'Nombre del usuario registrado.',
    example: 'juanito_dev',
  })
  @IsNotEmpty({ message: 'El nombre de usuario no puede estar vacío' })
  @IsString()
  user: string;

  @ApiProperty({
    description: 'Contraseña del usuario con al menos 8 caracteres.',
    example: 'contraseñaSegura123',
    minLength: 8,
  })
  @IsNotEmpty({ message: 'La contraseña no puede estar vacía' })
  @IsString()
  @MinLength(8, { message: 'La contraseña debe tener al menos 8 caracteres' })
  password: string;
}
