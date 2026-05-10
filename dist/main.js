"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const app_module_1 = require("./app.module");
const swagger_1 = require("@nestjs/swagger");
const config_1 = require("@nestjs/config");
const users_seeder_service_1 = require("./seeders/users-seeder/users-seeder.service");
const roles_seeder_service_1 = require("./seeders/roles-seeder/roles-seeder.service");
const common_1 = require("@nestjs/common");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.useGlobalPipes(new common_1.ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
    }));
    app.enableCors({
        origin: 'http://localhost:4200',
        methods: 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
        allowedHeaders: 'Content-Type, Authorization'
    });
    const rolesSeeder = await app.get(roles_seeder_service_1.RolesSeederService);
    await rolesSeeder.run();
    const userSeeder = await app.get(users_seeder_service_1.UsersSeederService);
    await userSeeder.run();
    const configervice = app.get(config_1.ConfigService);
    const options = new swagger_1.DocumentBuilder()
        .setTitle('smart-trash-backend')
        .setDescription('API del backend de Smart Trash Routes para gestionar camiones, empleados y rutas en tiempo real')
        .setVersion('2.0')
        .build();
    const document = swagger_1.SwaggerModule.createDocument(app, options);
    swagger_1.SwaggerModule.setup('doc', app, document);
    const PORT = configervice.get('PORT');
    app.setGlobalPrefix('api');
    await app.listen(PORT, '0.0.0.0');
    console.log('El servidor esta funcionando en el puerto: ', PORT);
}
bootstrap();
//# sourceMappingURL=main.js.map