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
Object.defineProperty(exports, "__esModule", { value: true });
exports.VehiculosService = void 0;
const common_1 = require("@nestjs/common");
let VehiculosService = class VehiculosService {
    constructor() { }
    data;
    async getAll() {
        const axios = require('axios');
        const response = await axios.get(process.env.API_URL + '/vehiculos/?perfil_id=' + process.env.API_KEY);
        return {
            msg: 'Vehículos encontrados exitosamente.',
            data: response.data
        };
    }
    async create(dto) {
        const axios = require('axios');
        const data = {
            ...dto,
            perfil_id: process.env.API_KEY,
            activo: true
        };
        try {
            const res = await axios.post(process.env.API_URL + '/vehiculos', data);
            return {
                msg: 'Vehículo registrado correctamente',
                data: res.data
            };
        }
        catch (err) {
            const backendMsg = err.response?.data?.message;
            if (backendMsg?.includes('placa has already been taken')) {
                return { msg: 'Esa placa ya está registrada.' };
            }
            return {
                msg: 'Error creando vehículo.',
                error: backendMsg || 'Error desconocido'
            };
        }
    }
    async findOne(id) {
        const axios = require('axios');
        const response = await axios.get(`${process.env.API_URL}/vehiculos/${id}?perfil_id=${process.env.API_KEY}`);
        return {
            msg: 'Vehículo encontrado exitosamente.',
            data: response.data
        };
    }
    async update(id, dto) {
        const axios = require('axios');
        const data = {
            ...dto,
            activo: true,
            perfil_id: process.env.API_KEY
        };
        const url = `${process.env.API_URL}/vehiculos/${id}`;
        const response = await axios.put(url, data);
        return {
            msg: 'Vehículo actualizado exitosamente.',
            data: response.data
        };
    }
    async remove(id) {
        const axios = require('axios');
        const url = `${process.env.API_URL}/vehiculos/${id}?perfil_id=${process.env.API_KEY}`;
        await axios.delete(url);
        return {
            msg: 'El vehículo se ha eliminado exitosamente.'
        };
    }
};
exports.VehiculosService = VehiculosService;
exports.VehiculosService = VehiculosService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [])
], VehiculosService);
//# sourceMappingURL=vehiculos.service.js.map