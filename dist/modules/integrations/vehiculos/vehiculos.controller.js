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
exports.VehiculosController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const vehiculos_service_1 = require("./vehiculos.service");
const jwt_guard_1 = require("../../../guard/jwt/jwt.guard");
const roles_guard_1 = require("../../../guard/roles/roles.guard");
const roles_decorator_1 = require("../../../common/decorators/roles.decorator");
let VehiculosController = class VehiculosController {
    vehiculosService;
    constructor(vehiculosService) {
        this.vehiculosService = vehiculosService;
    }
    getAll() {
        return this.vehiculosService.getAll();
    }
    create(body) {
        return this.vehiculosService.create(body);
    }
    findOne(id) {
        return this.vehiculosService.findOne(id);
    }
    update(id, body) {
        return this.vehiculosService.update(id, body);
    }
    remove(id) {
        return this.vehiculosService.remove(id);
    }
};
exports.VehiculosController = VehiculosController;
__decorate([
    (0, common_1.Get)('all'),
    (0, swagger_1.ApiOperation)({ summary: 'Obtener todos los vehículos' }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Lista de vehículos obtenida correctamente.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], VehiculosController.prototype, "getAll", null);
__decorate([
    (0, common_1.Post)('register'),
    (0, swagger_1.ApiOperation)({ summary: 'Registrar un nuevo vehículo' }),
    (0, swagger_1.ApiBody)({
        description: 'Datos enviados desde Postman (sin perfil_id)',
        schema: {
            example: {
                placa: 'XYZ-123',
                marca: 'Ford Fiesta',
                modelo: '2022'
            }
        }
    }),
    (0, swagger_1.ApiResponse)({
        status: 201,
        description: 'Vehículo registrado exitosamente.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 400,
        description: 'Error en los datos enviados.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], VehiculosController.prototype, "create", null);
__decorate([
    (0, common_1.Get)(':id'),
    (0, swagger_1.ApiOperation)({ summary: 'Obtener un vehículo por ID' }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Vehículo encontrado correctamente.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 404,
        description: 'Vehículo no encontrado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], VehiculosController.prototype, "findOne", null);
__decorate([
    (0, common_1.Put)(':id'),
    (0, swagger_1.ApiOperation)({ summary: 'Actualizar un vehículo existente' }),
    (0, swagger_1.ApiBody)({
        description: 'Datos a actualizar',
        schema: {
            example: {
                placa: 'XYZ-987',
                marca: 'Nissan Versa',
                modelo: '2023'
            }
        }
    }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Vehículo actualizado exitosamente.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 400,
        description: 'Datos inválidos enviados.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 404,
        description: 'Vehículo no encontrado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    }),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", void 0)
], VehiculosController.prototype, "update", null);
__decorate([
    (0, common_1.Delete)(':id'),
    (0, swagger_1.ApiOperation)({ summary: 'Eliminar un vehículo por ID' }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Vehículo eliminado exitosamente.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 404,
        description: 'Vehículo no encontrado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 401,
        description: 'No autorizado: JWT inválido o expirado.'
    }),
    (0, swagger_1.ApiResponse)({
        status: 403,
        description: 'Acceso denegado: No tienes rol ADMIN.'
    }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], VehiculosController.prototype, "remove", null);
exports.VehiculosController = VehiculosController = __decorate([
    (0, common_1.Controller)('vehiculos'),
    (0, common_1.UseGuards)(jwt_guard_1.JwtAuthGuard, roles_guard_1.RolesGuard),
    (0, roles_decorator_1.Roles)('ADMIN'),
    (0, swagger_1.ApiTags)('Vehiculos'),
    __metadata("design:paramtypes", [vehiculos_service_1.VehiculosService])
], VehiculosController);
//# sourceMappingURL=vehiculos.controller.js.map