import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ApiBody, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { RegisterService } from './register/register.service';
import { LoginService } from './login/login.service';
import { LogoutService } from './logout/logout.service';
import { CreateUserDto } from '../users/dto/create-user.dto';
import { LoginUserDto } from '../users/dto/login-user.dto';
import { JwtAuthGuard } from 'src/guard/jwt/jwt.guard';

@Controller('auth')
@ApiTags('Auth')
export class AuthController {
    constructor(
        private readonly registerService: RegisterService,
        private readonly loginService: LoginService,
        private readonly logoutService: LogoutService,
    ) { }
    @Post('register')
    @ApiOperation({ summary: 'Registro de usuario', description: 'Crea un nuevo usuario en el sistema.' })
    @ApiBody({
        description: 'Datos necesarios para registrar un usuario',
        type: CreateUserDto
    })
    @ApiResponse({
        status: 201,
        description: 'El usuario ha sido registrado exitosamente.',
        type: CreateUserDto
    })
    @ApiResponse({
        status: 409,
        description: 'El usuario ya existe.',
    })
    @ApiResponse({
        status: 500,
        description: 'Error interno del servidor.',
    })
    register(@Body() createUserDto: CreateUserDto) {
        return this.registerService.register(createUserDto);
    }
    @Post('login')
    @ApiOperation({ summary: 'Login de usuario' })
    @ApiBody({ type: LoginUserDto })
    @ApiResponse({ status: 200, description: 'Login exitoso' })
    @ApiResponse({ status: 401, description: 'Credenciales incorrectas' })
    login(@Body() loginUserDto: LoginUserDto) {
        return this.loginService.login(loginUserDto)
    }
    @Get('logout')
    @UseGuards(JwtAuthGuard)
    logout() {
        return this.logoutService.logout()
    }
}
