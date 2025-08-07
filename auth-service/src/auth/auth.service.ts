import { Injectable, UnauthorizedException, BadRequestException, ConflictException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import * as bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import { UsersService } from '../users/users.service';
import { SessionsService } from '../sessions/sessions.service';
import { EmailService } from '../email/email.service';
import { CacheService } from '../cache/cache.service';
import { RegisterDto } from './dto/register.dto';
import { User } from '../core/entities/user.entity';

@Injectable()
export class AuthService {
  constructor(
    private readonly usersService: UsersService,
    private readonly sessionsService: SessionsService,
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
    private readonly emailService: EmailService,
    private readonly cacheService: CacheService,
  ) {}

  async register(registerDto: RegisterDto) {
    // Check if user already exists
    const existingUser = await this.usersService.findByEmail(registerDto.email);
    if (existingUser) {
      throw new ConflictException('User with this email already exists');
    }

    // Hash password
    const passwordHash = await bcrypt.hash(registerDto.password, 12);

    // Create user
    const user = await this.usersService.create({
      email: registerDto.email,
      passwordHash,
      emailVerified: false,
    });

    // Send verification email
    const verificationToken = await this.generateVerificationToken(user.id);
    await this.emailService.sendVerificationEmail(user.email, verificationToken);

    // Generate tokens
    const tokens = await this.generateTokens(user);

    // Create session
    await this.sessionsService.create({
      userId: user.id,
      tokenFamily: uuidv4(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
    });

    return {
      user: this.sanitizeUser(user),
      tokens,
    };
  }

  async login(user: User, rememberMe: boolean, request: any) {
    // Check if 2FA is enabled
    if (user.mfaEnabled) {
      // Return partial token that requires 2FA verification
      const mfaToken = await this.generateMfaToken(user);
      return {
        requiresMfa: true,
        mfaToken,
      };
    }

    // Generate tokens
    const tokens = await this.generateTokens(user);

    // Create session
    const sessionExpiry = rememberMe
      ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days
      : new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

    await this.sessionsService.create({
      userId: user.id,
      tokenFamily: uuidv4(),
      expiresAt: sessionExpiry,
      ipAddress: request.ip,
      userAgent: request.headers['user-agent'],
    });

    // Update last login
    await this.usersService.updateLastLogin(user.id);

    return {
      user: this.sanitizeUser(user),
      tokens,
    };
  }

  async logout(userId: string, sessionId: string) {
    await this.sessionsService.revoke(sessionId, 'User logout');
    await this.cacheService.del(`session:${sessionId}`);
    return { message: 'Logged out successfully' };
  }

  async refreshTokens(refreshToken: string) {
    try {
      const payload = this.jwtService.verify(refreshToken, {
        secret: this.configService.get('JWT_REFRESH_SECRET'),
      });

      const user = await this.usersService.findById(payload.sub);
      if (!user) {
        throw new UnauthorizedException('Invalid refresh token');
      }

      const session = await this.sessionsService.findById(payload.sessionId);
      if (!session || !session.isActive) {
        throw new UnauthorizedException('Session expired or revoked');
      }

      // Rotate refresh token
      const tokens = await this.generateTokens(user, session.id);
      return { tokens };
    } catch (error) {
      throw new UnauthorizedException('Invalid refresh token');
    }
  }

  async verifyEmail(token: string) {
    const userId = await this.cacheService.get(`email-verify:${token}`);
    if (!userId) {
      throw new BadRequestException('Invalid or expired verification token');
    }

    await this.usersService.verifyEmail(userId);
    await this.cacheService.del(`email-verify:${token}`);

    return { message: 'Email verified successfully' };
  }

  async forgotPassword(email: string) {
    const user = await this.usersService.findByEmail(email);
    if (!user) {
      // Don't reveal if user exists
      return { message: 'If the email exists, a reset link has been sent' };
    }

    const resetToken = await this.generatePasswordResetToken(user.id);
    await this.emailService.sendPasswordResetEmail(user.email, resetToken);

    return { message: 'If the email exists, a reset link has been sent' };
  }

  async resetPassword(token: string, newPassword: string) {
    const userId = await this.cacheService.get(`password-reset:${token}`);
    if (!userId) {
      throw new BadRequestException('Invalid or expired reset token');
    }

    const passwordHash = await bcrypt.hash(newPassword, 12);
    await this.usersService.updatePassword(userId, passwordHash);
    await this.cacheService.del(`password-reset:${token}`);

    // Revoke all sessions for security
    await this.sessionsService.revokeAllForUser(userId);

    return { message: 'Password reset successfully' };
  }

  async verifyMfa(userId: string, code: string, type: string) {
    // Implementation depends on MFA service
    // This is a placeholder
    const isValid = await this.validateMfaCode(userId, code, type);
    if (!isValid) {
      throw new UnauthorizedException('Invalid MFA code');
    }

    const user = await this.usersService.findById(userId);
    const tokens = await this.generateTokens(user);

    return {
      user: this.sanitizeUser(user),
      tokens,
    };
  }

  async getUserSessions(userId: string) {
    return this.sessionsService.findActiveByUserId(userId);
  }

  async revokeSession(userId: string, sessionId: string) {
    const session = await this.sessionsService.findById(sessionId);
    if (!session || session.userId !== userId) {
      throw new BadRequestException('Session not found');
    }

    await this.sessionsService.revoke(sessionId, 'User requested');
    await this.cacheService.del(`session:${sessionId}`);

    return { message: 'Session revoked successfully' };
  }

  async revokeAllSessions(userId: string, currentSessionId: string) {
    await this.sessionsService.revokeAllForUser(userId, currentSessionId);
    return { message: 'All sessions revoked successfully' };
  }

  async getProfile(userId: string) {
    const user = await this.usersService.findById(userId);
    return this.sanitizeUser(user);
  }

  private async generateTokens(user: User, sessionId?: string) {
    const payload = {
      sub: user.id,
      email: user.email,
      roles: user.roles,
      sessionId: sessionId || uuidv4(),
      etsyShopId: user.etsyShopId,
    };

    const accessToken = this.jwtService.sign(payload);
    const refreshToken = this.jwtService.sign(payload, {
      secret: this.configService.get('JWT_REFRESH_SECRET'),
      expiresIn: '30d',
    });

    return {
      accessToken,
      refreshToken,
      expiresIn: 900, // 15 minutes
    };
  }

  private async generateMfaToken(user: User) {
    const payload = {
      sub: user.id,
      type: 'mfa',
      exp: Math.floor(Date.now() / 1000) + 300, // 5 minutes
    };

    return this.jwtService.sign(payload);
  }

  private async generateVerificationToken(userId: string): Promise<string> {
    const token = uuidv4();
    await this.cacheService.set(`email-verify:${token}`, userId, 86400); // 24 hours
    return token;
  }

  private async generatePasswordResetToken(userId: string): Promise<string> {
    const token = uuidv4();
    await this.cacheService.set(`password-reset:${token}`, userId, 3600); // 1 hour
    return token;
  }

  private async validateMfaCode(userId: string, code: string, type: string): Promise<boolean> {
    // Placeholder - implement actual MFA validation
    return true;
  }

  private sanitizeUser(user: User) {
    const { passwordHash, mfaSecret, mfaBackupCodes, ...sanitized } = user;
    return sanitized;
  }
}