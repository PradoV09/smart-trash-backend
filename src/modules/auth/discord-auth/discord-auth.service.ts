import { Injectable } from '@nestjs/common';

@Injectable()
export class DiscordAuthService {
    discordLogin(req) {
    if (!req.user) {
      return 'No user from discord';
    }

    return {
      message: 'User information from discord',
      user: req.user,
    };
  }
}
