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
exports.RutasController = void 0;
const roles_decorator_1 = require("../../../common/decorators/roles.decorator");
const jwt_guard_1 = require("../../../guard/jwt/jwt.guard");
const roles_guard_1 = require("../../../guard/roles/roles.guard");
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const rutas_service_1 = require("./rutas.service");
let RutasController = class RutasController {
    rutasService;
    constructor(rutasService) {
        this.rutasService = rutasService;
    }
    getAll() {
        return this.rutasService.getAll();
    }
    create(body) {
        return this.rutasService.create(body);
    }
    findOneBy(id) {
        return this.rutasService.finOneBy(id);
    }
};
exports.RutasController = RutasController;
__decorate([
    (0, common_1.Get)('all'),
    (0, swagger_1.ApiOperation)({ summary: 'Obtener todas las rutas' }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Listado completo de rutas.',
        schema: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    id: { type: 'string', example: '1d23fa0c-7780-4de1-9f90-cc8e5a19e9be' },
                    nombre_ruta: { type: 'string', example: 'Ruta Puerto – 3' },
                    calles_ids: {
                        type: 'array',
                        items: { type: 'string', format: 'uuid' },
                        example: [
                            '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                            'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                        ]
                    }
                }
            }
        }
    }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], RutasController.prototype, "getAll", null);
__decorate([
    (0, common_1.Post)('register'),
    (0, swagger_1.ApiOperation)({ summary: 'Registrar una nueva ruta' }),
    (0, swagger_1.ApiResponse)({
        status: 201,
        description: 'Ruta creada correctamente.',
    }),
    (0, swagger_1.ApiResponse)({
        status: 400,
        description: 'Datos inválidos.',
    }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                nombre_ruta: {
                    type: 'string',
                    example: 'Ruta Puerto – 3',
                },
                calles_ids: {
                    type: 'array',
                    items: { type: 'string', format: 'uuid' },
                    example: [
                        '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                        'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                    ]
                }
            },
            required: ['nombre_ruta', 'calles_ids']
        }
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], RutasController.prototype, "create", null);
__decorate([
    (0, common_1.Get)(':id'),
    (0, swagger_1.ApiOperation)({ summary: 'Obtener una ruta por ID' }),
    (0, swagger_1.ApiResponse)({
        status: 200,
        description: 'Ruta encontrada.',
        schema: {
            type: 'object',
            properties: {
                id: { type: 'string', example: '1d23fa0c-7780-4de1-9f90-cc8e5a19e9be' },
                nombre_ruta: { type: 'string', example: 'Ruta Puerto – 3' },
                calles_ids: {
                    type: 'array',
                    items: { type: 'string', format: 'uuid' },
                    example: [
                        '3f9c1b2e-4da7-4b7c-92ab-dc3d9ac8e21f',
                        'a27e9514-0f5c-4f86-9e33-8c1b548c93d2'
                    ]
                }
            }
        }
    }),
    (0, swagger_1.ApiResponse)({ status: 404, description: 'Ruta no encontrada.' }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], RutasController.prototype, "findOneBy", null);
exports.RutasController = RutasController = __decorate([
    (0, common_1.Controller)('rutas'),
    (0, common_1.UseGuards)(jwt_guard_1.JwtAuthGuard, roles_guard_1.RolesGuard),
    (0, roles_decorator_1.Roles)('ADMIN'),
    (0, swagger_1.ApiTags)('Rutas'),
    __metadata("design:paramtypes", [rutas_service_1.RutasService])
], RutasController);
//# sourceMappingURL=rutas.controller.js.map