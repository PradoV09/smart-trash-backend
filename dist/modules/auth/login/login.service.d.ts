import { LoginUserDto } from '@modules/users/dto/login-user.dto';
import { JwtService } from '@nestjs/jwt';
import { UsersService } from '@modules/users/users.service';
export declare class LoginService {
    private readonly usersService;
    private readonly jwtService;
    constructor(usersService: UsersService, jwtService: JwtService);
    login(dto: LoginUserDto): Promise<{
        accessToken: string;
        refreshToken: string;
        username: string;
        userrol: string;
    }>;
}
