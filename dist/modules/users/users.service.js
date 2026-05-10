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
exports.UsersService = void 0;
const common_1 = require("@nestjs/common");
const user_entity_1 = require("./entities/user.entity");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const bcrypt = require("bcrypt");
const roles_entity_1 = require("../../entities/roles.entity");
let UsersService = class UsersService {
    userRepository;
    roleRepository;
    constructor(userRepository, roleRepository) {
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
    }
    async create(dto) {
        const nameuser = dto.nameuser.toLowerCase().trim();
        const exists = await this.userRepository.findOneBy({ nameuser });
        if (exists)
            throw new common_1.ConflictException("Ese usuario ya existe.");
        const passwordHash = await bcrypt.hash(dto.password, 10);
        const defaultRole = await this.roleRepository.findOne({
            where: { nameRol: 'ADMIN' }
        });
        if (!defaultRole) {
            throw new common_1.ConflictException("No existe el rol USER en la BD.");
        }
        const user = this.userRepository.create({
            ...dto,
            nameuser,
            password: passwordHash,
            role: defaultRole,
        });
        return this.userRepository.save(user);
    }
    async findByName(nameuser) {
        return this.userRepository
            .createQueryBuilder('user')
            .leftJoinAndSelect('user.role', 'role')
            .addSelect('user.password')
            .where('user.nameuser = :name', { name: nameuser })
            .getOne();
    }
    async findById(id) {
        return this.userRepository.findOneBy({ id });
    }
    async updateRefreshToken(id, refreshToken) {
        await this.userRepository.update(id, { refreshToken });
    }
};
exports.UsersService = UsersService;
exports.UsersService = UsersService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(user_entity_1.User)),
    __param(1, (0, typeorm_1.InjectRepository)(roles_entity_1.Role)),
    __metadata("design:paramtypes", [typeorm_2.Repository,
        typeorm_2.Repository])
], UsersService);
//# sourceMappingURL=users.service.js.map