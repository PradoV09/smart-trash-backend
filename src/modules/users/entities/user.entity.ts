import { Role } from "@entities/roles.entity";
import { Column, CreateDateColumn, Entity, ManyToOne, PrimaryGeneratedColumn, UpdateDateColumn } from "typeorm";

@Entity('users')
export class User {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column({ unique: true })
    nameuser: string;

    @Column({ select: false })
    password: string;

    @Column({ type: 'text', nullable: true, select: false })
    refreshToken: string | null;

    @ManyToOne(() => Role, role => role.users)
    role: Role;

    @CreateDateColumn()
    createdAt: Date;

    @UpdateDateColumn()
    updatedAt: Date;
}
