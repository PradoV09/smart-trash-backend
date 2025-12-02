import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { User } from '@modules/users/entities/user.entity';
import { UsersService } from '@modules/users/users.service';
import { Repository } from 'typeorm';

@Injectable()
export class UsersSeederService {
    constructor(
        @InjectRepository(User)
        private readonly userRepository: Repository<User>,

        private readonly usersService: UsersService
    ) { }

    async run() {
        await this.userRepository.clear()

        const users = [
            { nameuser: 'admin', password: 'admin1234' },
            { nameuser: 'jose', password: 'jose1234' },
            { nameuser: 'heiner', password: 'heiner1234' },
            { nameuser: 'jonatan', password: 'jonatan1234' },
        ]
        for (const u of users) {
            await this.usersService.create(u);
        }
    }
}
