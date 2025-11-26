import { Injectable } from '@nestjs/common';
import { UsersService } from '@modules/users/users.service';

@Injectable()
export class LogoutService {
  constructor(private readonly usersService: UsersService) {}

  async logout(userId: string) {
    
    const user = await this.usersService.findById(userId)

    await this.usersService.updateRefreshToken(userId, null);

    return { message: 'Sesión cerrada correctamente' };
  }
}
