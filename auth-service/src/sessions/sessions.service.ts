import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, LessThan } from 'typeorm';
import { Session } from '../core/entities/session.entity';
import { Cron, CronExpression } from '@nestjs/schedule';

@Injectable()
export class SessionsService {
  constructor(
    @InjectRepository(Session)
    private sessionsRepository: Repository<Session>,
  ) {}

  async create(sessionData: Partial<Session>): Promise<Session> {
    const session = this.sessionsRepository.create(sessionData);
    return this.sessionsRepository.save(session);
  }

  async findById(id: string): Promise<Session | null> {
    return this.sessionsRepository.findOne({
      where: { id },
      relations: ['user'],
    });
  }

  async findActiveByUserId(userId: string): Promise<Session[]> {
    return this.sessionsRepository.find({
      where: {
        userId,
        isActive: true,
        expiresAt: LessThan(new Date()),
      },
      order: { createdAt: 'DESC' },
    });
  }

  async findByTokenFamily(tokenFamily: string): Promise<Session[]> {
    return this.sessionsRepository.find({
      where: { tokenFamily },
      order: { createdAt: 'DESC' },
    });
  }

  async revoke(id: string, reason: string): Promise<void> {
    await this.sessionsRepository.update(id, {
      isActive: false,
      revokedAt: new Date(),
      revokedReason: reason,
    });
  }

  async revokeByTokenFamily(tokenFamily: string, reason: string): Promise<void> {
    await this.sessionsRepository.update(
      { tokenFamily },
      {
        isActive: false,
        revokedAt: new Date(),
        revokedReason: reason,
      },
    );
  }

  async revokeAllForUser(userId: string, exceptSessionId?: string): Promise<void> {
    const query = this.sessionsRepository
      .createQueryBuilder()
      .update(Session)
      .set({
        isActive: false,
        revokedAt: new Date(),
        revokedReason: 'User requested logout from all devices',
      })
      .where('userId = :userId', { userId });

    if (exceptSessionId) {
      query.andWhere('id != :exceptId', { exceptId: exceptSessionId });
    }

    await query.execute();
  }

  async extendSession(id: string, expiresAt: Date): Promise<void> {
    await this.sessionsRepository.update(id, { expiresAt });
  }

  async updateLocation(id: string, location: any): Promise<void> {
    await this.sessionsRepository.update(id, { location });
  }

  async countActiveSessions(userId: string): Promise<number> {
    return this.sessionsRepository.count({
      where: {
        userId,
        isActive: true,
        expiresAt: LessThan(new Date()),
      },
    });
  }

  async getSessionStats(userId: string): Promise<{
    total: number;
    active: number;
    revoked: number;
  }> {
    const [total, active, revoked] = await Promise.all([
      this.sessionsRepository.count({ where: { userId } }),
      this.sessionsRepository.count({
        where: {
          userId,
          isActive: true,
          expiresAt: LessThan(new Date()),
        },
      }),
      this.sessionsRepository.count({
        where: {
          userId,
          isActive: false,
        },
      }),
    ]);

    return { total, active, revoked };
  }

  @Cron(CronExpression.EVERY_HOUR)
  async cleanupExpiredSessions(): Promise<void> {
    const result = await this.sessionsRepository.update(
      {
        isActive: true,
        expiresAt: LessThan(new Date()),
      },
      {
        isActive: false,
        revokedAt: new Date(),
        revokedReason: 'Session expired',
      },
    );

    console.log(`Cleaned up ${result.affected} expired sessions`);
  }

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async deleteOldSessions(): Promise<void> {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const result = await this.sessionsRepository.delete({
      createdAt: LessThan(thirtyDaysAgo),
      isActive: false,
    });

    console.log(`Deleted ${result.affected} old sessions`);
  }
}