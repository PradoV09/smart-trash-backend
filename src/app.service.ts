import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hola mundo, mi aplicación NestJS si funciona!';
  }
}
