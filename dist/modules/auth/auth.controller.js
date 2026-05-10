"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const register_service_1 = require("./register/register.service");
const login_service_1 = require("./login/login.service");
const logout_service_1 = require("./logout/logout.service");
const create_user_dto_1 = require("../users/dto/create-user.dto");
const login_user_dto_1 = require("../users/dto/login-user.dto");
const jwt_guard_1 = require("../../guard/jwt/jwt.guard");
let AuthController = class AuthController {
    registerService;
    loginService;
    logoutService;
    constructor(registerService, loginService, logoutService) {
        this.registerService = registerService;
        this.loginService = loginService;
        this.logoutService = logoutService;
    }
    register(createUserDto) {
        return this.registerService.register(createUserDto);
    }
    login(loginUserDto) {
        return this.loginService.login(loginUserDto);
    }
    logout(req) {
        return this.logoutService.logout(req.user.sub);
    }
};
exports.AuthController = AuthController;
__decorate([
    (0, common_1.Post)('register'),
    (0, swagger_1.ApiOperation)({ summary: 'Registro de usuario', description: 'Crea un nuevo usuario en el sistema.' }),
    (0, swagger_1.ApiBody)({
        description: 'Datos necesarios para registrar un usuario',
        type: create_user_dto_1.CreateUserDto
    }),
    (0, swagger_1.ApiResponse)({
        status: 201,
        description: 'El usuario ha sido registrado exitosamente.',
        type: create_user_dto_1.CreateUserDto
    }),
    (0, swagger_1.ApiResponse)({
        status: 409,
        description: 'El usuario ya existe.',
    }),
    (0, swagger_1.ApiResponse)({
        status: 500,
        description: 'Error interno del servidor.',
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [create_user_dto_1.CreateUserDto]),
    __metadata("design:returntype", void 0)
], AuthController.prototype, "register", null);
__decorate([
    (0, common_1.Post)('login'),
    (0, swagger_1.ApiOperation)({ summary: 'Login de usuario' }),
    (0, swagger_1.ApiBody)({ type: login_user_dto_1.LoginUserDto }),
    (0, swagger_1.ApiResponse)({ status: 200, description: 'Login exitoso' }),
    (0, swagger_1.ApiResponse)({ status: 401, description: 'Credenciales incorrectas' }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [login_user_dto_1.LoginUserDto]),
    __metadata("design:returntype", void 0)
], AuthController.prototype, "login", null);
__decorate([
    (0, common_1.Post)('logout'),
    (0, swagger_1.ApiOperation)({ summary: 'Cerrar sesión' }),
    (0, swagger_1.ApiResponse)({ status: 200, description: 'Logout exitoso' }),
    (0, common_1.UseGuards)(jwt_guard_1.JwtAuthGuard),
    __param(0, (0, common_1.Req)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], AuthController.prototype, "logout", null);
exports.AuthController = AuthController = __decorate([
    (0, common_1.Controller)('auth'),
    (0, swagger_1.ApiTags)('Auth'),
    __metadata("design:paramtypes", [register_service_1.RegisterService,
        login_service_1.LoginService,
        logout_service_1.LogoutService])
], AuthController);
//# sourceMappingURL=auth.controller.js.map