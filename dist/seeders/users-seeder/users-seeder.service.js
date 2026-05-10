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
exports.UsersSeederService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const user_entity_1 = require("../../modules/users/entities/user.entity");
const users_service_1 = require("../../modules/users/users.service");
const typeorm_2 = require("typeorm");
let UsersSeederService = class UsersSeederService {
    userRepository;
    usersService;
    constructor(userRepository, usersService) {
        this.userRepository = userRepository;
        this.usersService = usersService;
    }
    async run() {
        const users = [
            { nameuser: 'admin', password: 'admin1234' },
            { nameuser: 'jose', password: 'jose1234' },
            { nameuser: 'heiner', password: 'heiner1234' },
            { nameuser: 'jonatan', password: 'jonatan1234' },
            { nameuser: 'GlucioProfe', password: 'elprogoat' },
        ];
        for (const u of users) {
            await this.usersService.create(u);
        }
    }
};
exports.UsersSeederService = UsersSeederService;
exports.UsersSeederService = UsersSeederService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(user_entity_1.User)),
    __metadata("design:paramtypes", [typeorm_2.Repository,
        users_service_1.UsersService])
], UsersSeederService);
//# sourceMappingURL=users-seeder.service.js.map