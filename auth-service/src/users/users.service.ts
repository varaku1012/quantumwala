import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User, UserRole } from '../core/entities/user.entity';
import { MfaType } from '../mfa/mfa.service';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private usersRepository: Repository<User>,
  ) {}

  async create(userData: Partial<User>): Promise<User> {
    const user = this.usersRepository.create(userData);
    return this.usersRepository.save(user);
  }

  async findById(id: string): Promise<User | null> {
    return this.usersRepository.findOne({ where: { id } });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.usersRepository.findOne({ where: { email } });
  }

  async findByEtsyUserId(etsyUserId: string): Promise<User | null> {
    return this.usersRepository.findOne({ where: { etsyUserId } });
  }

  async update(id: string, updateData: Partial<User>): Promise<void> {
    await this.usersRepository.update(id, updateData);
  }

  async updateLastLogin(id: string): Promise<void> {
    await this.usersRepository.update(id, { lastLoginAt: new Date() });
  }

  async verifyEmail(id: string): Promise<void> {
    await this.usersRepository.update(id, { emailVerified: true });
  }

  async updatePassword(id: string, passwordHash: string): Promise<void> {
    await this.usersRepository.update(id, { passwordHash });
  }

  async enableMfa(id: string, type: MfaType, backupCodes: string[]): Promise<void> {
    const secret = await this.generateMfaSecret(type);
    
    await this.usersRepository.update(id, {
      mfaEnabled: true,
      mfaSecret: secret,
      mfaBackupCodes: backupCodes,
      metadata: this.usersRepository
        .createQueryBuilder()
        .update(User)
        .set({
          metadata: () => `metadata || '{"mfaType": "${type}"}'::jsonb`,
        })
        .where('id = :id', { id })
        .getSql(),
    });
  }

  async disableMfa(id: string): Promise<void> {
    await this.usersRepository.update(id, {
      mfaEnabled: false,
      mfaSecret: null,
      mfaBackupCodes: null,
    });
  }

  async updateBackupCodes(id: string, backupCodes: string[]): Promise<void> {
    await this.usersRepository.update(id, { mfaBackupCodes: backupCodes });
  }

  async updateRoles(id: string, roles: UserRole[]): Promise<void> {
    await this.usersRepository.update(id, { roles });
  }

  async delete(id: string): Promise<void> {
    await this.usersRepository.softDelete(id);
  }

  async findActiveUsers(limit: number = 100, offset: number = 0): Promise<[User[], number]> {
    return this.usersRepository.findAndCount({
      where: { accountStatus: 'active' },
      take: limit,
      skip: offset,
      order: { createdAt: 'DESC' },
    });
  }

  async countByStatus(status: string): Promise<number> {
    return this.usersRepository.count({ where: { accountStatus: status as any } });
  }

  private async generateMfaSecret(type: MfaType): Promise<string> {
    // For TOTP, the secret will be stored when verified
    // For SMS/Email, no secret is needed
    return type === MfaType.TOTP ? '' : null;
  }
}