import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
  Index,
  Unique,
} from 'typeorm';
import { User } from './user.entity';

export enum OAuthProvider {
  ETSY = 'etsy',
}

@Entity('oauth_tokens')
@Unique(['userId', 'provider'])
export class OAuthToken {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  @Index()
  userId: string;

  @Column({
    type: 'enum',
    enum: OAuthProvider,
  })
  provider: OAuthProvider;

  @Column({ type: 'text' })
  accessToken: string;

  @Column({ type: 'text', nullable: true })
  refreshToken: string;

  @Column({ nullable: true })
  @Index()
  expiresAt: Date;

  @Column('text', { array: true, nullable: true })
  scopes: string[];

  @Column({ nullable: true })
  providerUserId: string;

  @Column('jsonb', { nullable: true })
  providerData: Record<string, any>;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  @ManyToOne(() => User, (user) => user.oauthTokens)
  @JoinColumn({ name: 'userId' })
  user: User;
}