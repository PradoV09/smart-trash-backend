import { Controller, Get, Req, UseGuards } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { GoogleAuthGuard } from 'src/guard/google/google.guard';
import { AuthService } from './auth.service';
import { DiscordGuard } from 'src/guard/discord/discord.guard';

@ApiTags('Auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  // /api/auth/google/login
  @Get('google/login')
  @UseGuards(GoogleAuthGuard)
  @ApiOperation({ summary: 'Iniciar sesion con google' })
  async googleLogin() {
    return;
  }

  // /api/auth/google/redirect
  @Get('google/redirect')
  @UseGuards(GoogleAuthGuard)
  @ApiOperation({
    summary: 'Redirige al usuario a Google para iniciar sesión (OAuth2)',
  })
  async googleRedirect(@Req() req) {
    return req.user;
  }

  // /api/auth/google/profile
  @Get('google/profile')
  @UseGuards(GoogleAuthGuard)
  @ApiOperation({ summary: 'Obtener datos de perfil de google' })
  googleProfile() {
    return 'Tus datos son:';
  }

  // /api/auth/google/logout
  @Get('google/logout')
  @UseGuards(GoogleAuthGuard)
  @ApiOperation({ summary: 'Cerrar sesion de google' })
  googleLogOut() {
    return 'Hasta pronto...';
  }

  // /api/auth/discord/redirect
  @Get('discord/login')
  @UseGuards(DiscordGuard)
  @ApiOperation({ summary: 'Iniciar sesion con discord' })
  async discordLogin() {
    return;
  }

  @Get('discord/redirect')
  @UseGuards(DiscordGuard)
  async discordRedirect(@Req() req) {
    return this.authService.discordLogin(req);
  }
}
