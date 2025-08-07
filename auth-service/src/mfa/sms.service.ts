import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as twilio from 'twilio';

@Injectable()
export class SmsService {
  private twilioClient: twilio.Twilio;

  constructor(private configService: ConfigService) {
    const accountSid = this.configService.get('TWILIO_ACCOUNT_SID');
    const authToken = this.configService.get('TWILIO_AUTH_TOKEN');
    
    if (accountSid && authToken) {
      this.twilioClient = twilio(accountSid, authToken);
    }
  }

  async sendCode(phoneNumber: string, code: string): Promise<void> {
    if (!this.twilioClient) {
      console.warn('Twilio not configured, skipping SMS send');
      return;
    }

    const fromNumber = this.configService.get('TWILIO_FROM_NUMBER');
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';

    try {
      await this.twilioClient.messages.create({
        body: `Your ${appName} verification code is: ${code}. Valid for 5 minutes.`,
        from: fromNumber,
        to: phoneNumber,
      });
    } catch (error) {
      console.error('Failed to send SMS:', error);
      throw new Error('Failed to send SMS verification code');
    }
  }

  async sendSecurityAlert(phoneNumber: string, message: string): Promise<void> {
    if (!this.twilioClient) {
      return;
    }

    const fromNumber = this.configService.get('TWILIO_FROM_NUMBER');
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';

    try {
      await this.twilioClient.messages.create({
        body: `${appName} Security Alert: ${message}`,
        from: fromNumber,
        to: phoneNumber,
      });
    } catch (error) {
      console.error('Failed to send security alert SMS:', error);
    }
  }
}