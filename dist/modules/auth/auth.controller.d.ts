import { RegisterService } from './register/register.service';
import { LoginService } from './login/login.service';
import { LogoutService } from './logout/logout.service';
import { CreateUserDto } from '../users/dto/create-user.dto';
import { LoginUserDto } from '../users/dto/login-user.dto';
export declare class AuthController {
    private readonly registerService;
    private readonly loginService;
    private readonly logoutService;
    constructor(registerService: RegisterService, loginService: LoginService, logoutService: LogoutService);
    register(createUserDto: CreateUserDto): Promise<{
        message: string;
        id: string;
        username: string;
    }>;
    login(loginUserDto: LoginUserDto): Promise<{
        accessToken: string;
        refreshToken: string;
        username: string;
        userrol: string;
    }>;
    logout(req: any): Promise<{
        message: string;
    }>;
}
