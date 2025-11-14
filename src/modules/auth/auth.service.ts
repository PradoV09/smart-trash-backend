import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
  googleLogin(req) {
    if (!req.user) {
      return 'No user from google';
    }

    return {
      message: 'User information from google',
      user: req.user,
    };
  }

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
