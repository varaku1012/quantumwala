import { Injectable, BadRequestException, UnauthorizedException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import * as crypto from 'crypto';
import { UsersService } from '../users/users.service';
import { TotpService } from './totp.service';
import { SmsService } from './sms.service';
import { EmailService } from '../email/email.service';
import { CacheService } from '../cache/cache.service';

export enum MfaType {
  TOTP = 'totp',
  SMS = 'sms',
  EMAIL = 'email',
}

@Injectable()
export class MfaService {
  constructor(
    private usersService: UsersService,
    private totpService: TotpService,
    private smsService: SmsService,
    private emailService: EmailService,
    private cacheService: CacheService,
  ) {}

  async enableMfa(userId: string, type: MfaType) {
    const user = await this.usersService.findById(userId);

    if (user.mfaEnabled) {
      throw new BadRequestException('MFA is already enabled');
    }

    switch (type) {
      case MfaType.TOTP:
        return this.setupTotp(userId);
      case MfaType.SMS:
        return this.setupSms(userId);
      case MfaType.EMAIL:
        return this.setupEmail(userId);
      default:
        throw new BadRequestException('Invalid MFA type');
    }
  }

  async verifySetup(userId: string, code: string, type: MfaType) {
    const isValid = await this.verifyCode(userId, code, type);

    if (!isValid) {
      throw new BadRequestException('Invalid verification code');
    }

    // Enable MFA and generate backup codes
    const backupCodes = this.generateBackupCodes();
    await this.usersService.enableMfa(userId, type, backupCodes);

    return {
      message: 'MFA enabled successfully',
      backupCodes,
    };
  }

  async disableMfa(userId: string, password: string) {
    const user = await this.usersService.findById(userId);

    if (!user.mfaEnabled) {
      throw new BadRequestException('MFA is not enabled');
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid password');
    }

    await this.usersService.disableMfa(userId);

    return { message: 'MFA disabled successfully' };
  }

  async verifyCode(userId: string, code: string, type: MfaType): Promise<boolean> {
    const user = await this.usersService.findById(userId);

    // Check if it's a backup code
    if (user.mfaBackupCodes && user.mfaBackupCodes.includes(code)) {
      // Remove used backup code
      const updatedCodes = user.mfaBackupCodes.filter(c => c !== code);
      await this.usersService.updateBackupCodes(userId, updatedCodes);
      return true;
    }

    switch (type) {
      case MfaType.TOTP:
        return this.totpService.verifyToken(user.mfaSecret, code);
      case MfaType.SMS:
      case MfaType.EMAIL:
        return this.verifyTemporaryCode(userId, code);
      default:
        return false;
    }
  }

  async sendMfaCode(userId: string, type: string) {
    const user = await this.usersService.findById(userId);

    if (!user.mfaEnabled) {
      throw new BadRequestException('MFA is not enabled');
    }

    const code = this.generateTemporaryCode();
    await this.cacheService.set(`mfa:${userId}:code`, code, 300); // 5 minutes

    switch (type) {
      case MfaType.SMS:
        await this.smsService.sendCode(user.metadata.phoneNumber, code);
        break;
      case MfaType.EMAIL:
        await this.emailService.sendMfaCode(user.email, code);
        break;
      default:
        throw new BadRequestException('Invalid MFA type');
    }

    return { message: 'Code sent successfully' };
  }

  async getBackupCodes(userId: string) {
    const user = await this.usersService.findById(userId);

    if (!user.mfaEnabled) {
      throw new BadRequestException('MFA is not enabled');
    }

    return {
      backupCodes: user.mfaBackupCodes || [],
      remaining: user.mfaBackupCodes?.length || 0,
    };
  }

  async regenerateBackupCodes(userId: string) {
    const user = await this.usersService.findById(userId);

    if (!user.mfaEnabled) {
      throw new BadRequestException('MFA is not enabled');
    }

    const backupCodes = this.generateBackupCodes();
    await this.usersService.updateBackupCodes(userId, backupCodes);

    return {
      message: 'Backup codes regenerated successfully',
      backupCodes,
    };
  }

  private async setupTotp(userId: string) {
    const secret = this.totpService.generateSecret();
    const qrCodeUrl = await this.totpService.generateQrCode(userId, secret);

    // Temporarily store secret until verification
    await this.cacheService.set(`mfa:${userId}:secret`, secret, 600); // 10 minutes

    return {
      type: MfaType.TOTP,
      secret,
      qrCode: qrCodeUrl,
      message: 'Scan the QR code with your authenticator app',
    };
  }

  private async setupSms(userId: string) {
    const user = await this.usersService.findById(userId);

    if (!user.metadata.phoneNumber) {
      throw new BadRequestException('Phone number is required for SMS MFA');
    }

    const code = this.generateTemporaryCode();
    await this.cacheService.set(`mfa:${userId}:setup`, code, 300); // 5 minutes
    await this.smsService.sendCode(user.metadata.phoneNumber, code);

    return {
      type: MfaType.SMS,
      phoneNumber: this.maskPhoneNumber(user.metadata.phoneNumber),
      message: 'Verification code sent to your phone',
    };
  }

  private async setupEmail(userId: string) {
    const user = await this.usersService.findById(userId);
    const code = this.generateTemporaryCode();
    
    await this.cacheService.set(`mfa:${userId}:setup`, code, 300); // 5 minutes
    await this.emailService.sendMfaCode(user.email, code);

    return {
      type: MfaType.EMAIL,
      email: this.maskEmail(user.email),
      message: 'Verification code sent to your email',
    };
  }

  private async verifyTemporaryCode(userId: string, code: string): Promise<boolean> {
    const storedCode = await this.cacheService.get(`mfa:${userId}:code`);
    const setupCode = await this.cacheService.get(`mfa:${userId}:setup`);

    return code === storedCode || code === setupCode;
  }

  private generateTemporaryCode(): string {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  private generateBackupCodes(): string[] {
    const codes: string[] = [];
    for (let i = 0; i < 10; i++) {
      const code = crypto.randomBytes(4).toString('hex').toUpperCase();
      codes.push(`${code.slice(0, 4)}-${code.slice(4)}`);
    }
    return codes;
  }

  private maskPhoneNumber(phone: string): string {
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  }

  private maskEmail(email: string): string {
    const [name, domain] = email.split('@');
    const maskedName = name.slice(0, 2) + '***';
    return `${maskedName}@${domain}`;
  }
}