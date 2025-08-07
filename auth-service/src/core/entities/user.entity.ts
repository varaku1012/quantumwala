import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  DeleteDateColumn,
  Index,
  OneToMany,
} from 'typeorm';
import { Session } from './session.entity';
import { OAuthToken } from './oauth-token.entity';

export enum AccountStatus {
  ACTIVE = 'active',
  SUSPENDED = 'suspended',
  DELETED = 'deleted',
}

export enum UserRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  ANALYST = 'analyst',
  OPERATOR = 'operator',
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  @Index()
  email: string;

  @Column({ default: false })
  emailVerified: boolean;

  @Column({ nullable: true })
  passwordHash: string;

  @Column({ nullable: true, unique: true })
  etsyUserId: string;

  @Column({ nullable: true })
  @Index()
  etsyShopId: string;

  @Column({ default: false })
  mfaEnabled: boolean;

  @Column({ nullable: true })
  mfaSecret: string;

  @Column('jsonb', { nullable: true })
  mfaBackupCodes: string[];

  @Column({
    type: 'enum',
    enum: AccountStatus,
    default: AccountStatus.ACTIVE,
  })
  @Index()
  accountStatus: AccountStatus;

  @Column('text', { array: true, default: [UserRole.OPERATOR] })
  roles: UserRole[];

  @Column('jsonb', { default: {} })
  metadata: Record<string, any>;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @Column({ nullable: true })
  lastLoginAt: Date;

  @DeleteDateColumn()
  deletedAt: Date;

  @OneToMany(() => Session, (session) => session.user)
  sessions: Session[];

  @OneToMany(() => OAuthToken, (token) => token.user)
  oauthTokens: OAuthToken[];
}