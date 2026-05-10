"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AppModule = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const config_1 = require("@nestjs/config");
const auth_module_1 = require("./modules/auth/auth.module");
const users_module_1 = require("./modules/users/users.module");
const roles_seeder_module_1 = require("./seeders/roles-seeder/roles-seeder.module");
const users_seeder_module_1 = require("./seeders/users-seeder/users-seeder.module");
const vehiculos_service_1 = require("./modules/integrations/vehiculos/vehiculos.service");
const vehiculos_controller_1 = require("./modules/integrations/vehiculos/vehiculos.controller");
const vehiculos_module_1 = require("./modules/integrations/vehiculos/vehiculos.module");
const rutas_module_1 = require("./modules/integrations/rutas/rutas.module");
let AppModule = class AppModule {
};
exports.AppModule = AppModule;
exports.AppModule = AppModule = __decorate([
    (0, common_1.Module)({
        imports: [
            config_1.ConfigModule.forRoot({ isGlobal: true }),
            typeorm_1.TypeOrmModule.forRoot({
                type: 'postgres',
                host: process.env.DB_HOST,
                port: Number(process.env.DB_PORT),
                username: process.env.DB_USER,
                password: process.env.DB_PASSWORD,
                database: process.env.DB_NAME,
                entities: [__dirname + '/**/*.entity{.ts,.js}'],
                synchronize: process.env.NODE_ENV !== 'production',
            }),
            auth_module_1.AuthModule,
            users_module_1.UsersModule,
            roles_seeder_module_1.RolesSeederModule,
            users_seeder_module_1.UsersSeederModule,
            vehiculos_module_1.VehiculosModule,
            rutas_module_1.RutasModule
        ],
        controllers: [vehiculos_controller_1.VehiculosController],
        providers: [vehiculos_service_1.VehiculosService],
    })
], AppModule);
//# sourceMappingURL=app.module.js.map