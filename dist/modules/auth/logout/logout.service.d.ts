import { UsersService } from '@modules/users/users.service';
export declare class LogoutService {
    private readonly usersService;
    constructor(usersService: UsersService);
    logout(userId: string): Promise<{
        message: string;
    }>;
}
