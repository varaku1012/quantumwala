import { Injectable } from '@nestjs/common';
import * as speakeasy from 'speakeasy';
import * as QRCode from 'qrcode';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class TotpService {
  constructor(private configService: ConfigService) {}

  generateSecret(): string {
    const secret = speakeasy.generateSecret({
      length: 32,
      name: this.configService.get('APP_NAME') || 'EtsyPro AI',
      issuer: 'EtsyPro',
    });

    return secret.base32;
  }

  async generateQrCode(userId: string, secret: string): Promise<string> {
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';
    const otpauthUrl = speakeasy.otpauthURL({
      secret: secret,
      label: `${appName}:${userId}`,
      issuer: 'EtsyPro',
      encoding: 'base32',
    });

    const qrCodeDataUrl = await QRCode.toDataURL(otpauthUrl);
    return qrCodeDataUrl;
  }

  verifyToken(secret: string, token: string): boolean {
    return speakeasy.totp.verify({
      secret: secret,
      encoding: 'base32',
      token: token,
      window: 2, // Allow 2 time steps before/after
    });
  }

  generateToken(secret: string): string {
    return speakeasy.totp({
      secret: secret,
      encoding: 'base32',
    });
  }
}