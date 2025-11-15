import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class GoogleAuthService {
  constructor(private jwtService: JwtService) {}

  googleLogin(req) {
    if (!req.user) {
      return 'No user from google';
    }

    const payload = {
      sub: req.user.id,      
      email: req.user.email, 
      name: req.user.name,
    };

    const token = this.jwtService.sign(payload);


    return {
      message: 'User information from google',
      user: req.user,
    };
  }
}
