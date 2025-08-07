import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as sgMail from '@sendgrid/mail';

@Injectable()
export class EmailService {
  constructor(private configService: ConfigService) {
    const apiKey = this.configService.get('SENDGRID_API_KEY');
    if (apiKey) {
      sgMail.setApiKey(apiKey);
    }
  }

  async sendVerificationEmail(email: string, token: string): Promise<void> {
    const frontendUrl = this.configService.get('FRONTEND_URL');
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';
    const verificationUrl = `${frontendUrl}/auth/verify-email?token=${token}`;

    const msg = {
      to: email,
      from: this.configService.get('EMAIL_FROM') || 'noreply@etsypro.ai',
      subject: `Verify your ${appName} account`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Welcome to ${appName}!</h2>
          <p>Please verify your email address to complete your registration.</p>
          <p style="margin: 20px 0;">
            <a href="${verificationUrl}" 
               style="background-color: #5469d4; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
              Verify Email Address
            </a>
          </p>
          <p>Or copy and paste this link into your browser:</p>
          <p style="word-break: break-all; color: #666;">${verificationUrl}</p>
          <p style="color: #666; font-size: 14px; margin-top: 40px;">
            This link will expire in 24 hours. If you didn't create an account, 
            you can safely ignore this email.
          </p>
        </div>
      `,
    };

    try {
      await sgMail.send(msg);
    } catch (error) {
      console.error('Failed to send verification email:', error);
      throw new Error('Failed to send verification email');
    }
  }

  async sendPasswordResetEmail(email: string, token: string): Promise<void> {
    const frontendUrl = this.configService.get('FRONTEND_URL');
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';
    const resetUrl = `${frontendUrl}/auth/reset-password?token=${token}`;

    const msg = {
      to: email,
      from: this.configService.get('EMAIL_FROM') || 'noreply@etsypro.ai',
      subject: `Reset your ${appName} password`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Password Reset Request</h2>
          <p>We received a request to reset your password for your ${appName} account.</p>
          <p style="margin: 20px 0;">
            <a href="${resetUrl}" 
               style="background-color: #5469d4; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
              Reset Password
            </a>
          </p>
          <p>Or copy and paste this link into your browser:</p>
          <p style="word-break: break-all; color: #666;">${resetUrl}</p>
          <p style="color: #666; font-size: 14px; margin-top: 40px;">
            This link will expire in 1 hour. If you didn't request a password reset, 
            you can safely ignore this email. Your password won't be changed.
          </p>
        </div>
      `,
    };

    try {
      await sgMail.send(msg);
    } catch (error) {
      console.error('Failed to send password reset email:', error);
      throw new Error('Failed to send password reset email');
    }
  }

  async sendMfaCode(email: string, code: string): Promise<void> {
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';

    const msg = {
      to: email,
      from: this.configService.get('EMAIL_FROM') || 'noreply@etsypro.ai',
      subject: `Your ${appName} verification code`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Verification Code</h2>
          <p>Your verification code for ${appName} is:</p>
          <p style="font-size: 32px; font-weight: bold; color: #5469d4; 
                    letter-spacing: 8px; margin: 20px 0;">
            ${code}
          </p>
          <p style="color: #666; font-size: 14px;">
            This code will expire in 5 minutes. If you didn't request this code, 
            please secure your account immediately.
          </p>
        </div>
      `,
    };

    try {
      await sgMail.send(msg);
    } catch (error) {
      console.error('Failed to send MFA code email:', error);
      throw new Error('Failed to send MFA code email');
    }
  }

  async sendWelcomeEmail(email: string, name?: string): Promise<void> {
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';
    const frontendUrl = this.configService.get('FRONTEND_URL');

    const msg = {
      to: email,
      from: this.configService.get('EMAIL_FROM') || 'noreply@etsypro.ai',
      subject: `Welcome to ${appName}!`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Welcome to ${appName}${name ? ', ' + name : ''}!</h2>
          <p>Your account has been successfully created.</p>
          <p>Here's what you can do next:</p>
          <ul style="line-height: 2;">
            <li>Connect your Etsy shop to start optimizing</li>
            <li>Enable two-factor authentication for extra security</li>
            <li>Explore our AI-powered tools for Etsy sellers</li>
          </ul>
          <p style="margin: 20px 0;">
            <a href="${frontendUrl}/dashboard" 
               style="background-color: #5469d4; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
              Go to Dashboard
            </a>
          </p>
          <p style="color: #666; font-size: 14px; margin-top: 40px;">
            If you have any questions, feel free to reach out to our support team.
          </p>
        </div>
      `,
    };

    try {
      await sgMail.send(msg);
    } catch (error) {
      console.error('Failed to send welcome email:', error);
    }
  }

  async sendSecurityAlert(email: string, subject: string, message: string): Promise<void> {
    const appName = this.configService.get('APP_NAME') || 'EtsyPro AI';

    const msg = {
      to: email,
      from: this.configService.get('EMAIL_FROM') || 'noreply@etsypro.ai',
      subject: `${appName} Security Alert: ${subject}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #d32f2f;">Security Alert</h2>
          <p>${message}</p>
          <p style="margin: 20px 0;">
            If this was you, you can safely ignore this message. 
            If not, please secure your account immediately.
          </p>
          <p style="color: #666; font-size: 14px; margin-top: 40px;">
            This is an automated security notification from ${appName}.
          </p>
        </div>
      `,
    };

    try {
      await sgMail.send(msg);
    } catch (error) {
      console.error('Failed to send security alert:', error);
    }
  }
}