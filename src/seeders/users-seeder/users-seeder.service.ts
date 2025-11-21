import { Injectable } from '@nestjs/common';
import { UsersService } from 'src/modules/users/users.service';

@Injectable()
export class UsersSeederService {
  constructor(private readonly usersService: UsersService) {}

  async Run() {
    const usuarios = [
      { user: 'jose', password: 'jose1234' },
      { user: 'heiner', password: 'heiner1234' },
      { user: 'jonatan', password: 'jonatan1234' },
      { user: 'admin', password: 'admin1234' },
    ];

    for (const u of usuarios) {
      await this.usersService.create(u);
    }
  }
}
