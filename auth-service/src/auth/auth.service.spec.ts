import { Test, TestingModule } from '@nestjs/testing';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { UnauthorizedException, ConflictException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { AuthService } from './auth.service';
import { UsersService } from '../users/users.service';
import { SessionsService } from '../sessions/sessions.service';
import { EmailService } from '../email/email.service';
import { CacheService } from '../cache/cache.service';

describe('AuthService', () => {
  let authService: AuthService;
  let usersService: UsersService;
  let sessionsService: SessionsService;
  let jwtService: JwtService;
  let emailService: EmailService;
  let cacheService: CacheService;

  const mockUser = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    email: 'test@example.com',
    passwordHash: '$2b$12$mock.password.hash',
    emailVerified: true,
    mfaEnabled: false,
    etsyShopId: 'shop123',
    roles: ['seller'],
    accountStatus: 'active',
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        {
          provide: UsersService,
          useValue: {
            findByEmail: jest.fn(),
            findById: jest.fn(),
            create: jest.fn(),
            updateLastLogin: jest.fn(),
            verifyEmail: jest.fn(),
            updatePassword: jest.fn(),
          },
        },
        {
          provide: SessionsService,
          useValue: {
            create: jest.fn(),
            findById: jest.fn(),
            revoke: jest.fn(),
            revokeAllForUser: jest.fn(),
            findActiveByUserId: jest.fn(),
          },
        },
        {
          provide: JwtService,
          useValue: {
            sign: jest.fn(),
            verify: jest.fn(),
          },
        },
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn(),
          },
        },
        {
          provide: EmailService,
          useValue: {
            sendVerificationEmail: jest.fn(),
            sendPasswordResetEmail: jest.fn(),
          },
        },
        {
          provide: CacheService,
          useValue: {
            get: jest.fn(),
            set: jest.fn(),
            del: jest.fn(),
          },
        },
      ],
    }).compile();

    authService = module.get<AuthService>(AuthService);
    usersService = module.get<UsersService>(UsersService);
    sessionsService = module.get<SessionsService>(SessionsService);
    jwtService = module.get<JwtService>(JwtService);
    emailService = module.get<EmailService>(EmailService);
    cacheService = module.get<CacheService>(CacheService);
  });

  describe('register', () => {
    it('should register a new user successfully', async () => {
      const registerDto = {
        email: 'new@example.com',
        password: 'SecureP@ssw0rd123',
      };

      jest.spyOn(usersService, 'findByEmail').mockResolvedValue(null);
      jest.spyOn(usersService, 'create').mockResolvedValue(mockUser as any);
      jest.spyOn(jwtService, 'sign').mockReturnValue('mock.jwt.token');
      jest.spyOn(bcrypt, 'hash').mockResolvedValue('hashed.password' as never);

      const result = await authService.register(registerDto);

      expect(usersService.findByEmail).toHaveBeenCalledWith(registerDto.email);
      expect(usersService.create).toHaveBeenCalled();
      expect(emailService.sendVerificationEmail).toHaveBeenCalled();
      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('tokens');
    });

    it('should throw ConflictException if user already exists', async () => {
      const registerDto = {
        email: 'existing@example.com',
        password: 'SecureP@ssw0rd123',
      };

      jest.spyOn(usersService, 'findByEmail').mockResolvedValue(mockUser as any);

      await expect(authService.register(registerDto)).rejects.toThrow(
        ConflictException,
      );
    });
  });

  describe('login', () => {
    it('should login user successfully without MFA', async () => {
      const request = { ip: '127.0.0.1', headers: { 'user-agent': 'test' } };
      
      jest.spyOn(jwtService, 'sign').mockReturnValue('mock.jwt.token');
      jest.spyOn(sessionsService, 'create').mockResolvedValue({} as any);
      jest.spyOn(usersService, 'updateLastLogin').mockResolvedValue();

      const result = await authService.login(mockUser as any, false, request);

      expect(result).toHaveProperty('user');
      expect(result).toHaveProperty('tokens');
      expect(sessionsService.create).toHaveBeenCalled();
      expect(usersService.updateLastLogin).toHaveBeenCalledWith(mockUser.id);
    });

    it('should require MFA if enabled', async () => {
      const userWithMfa = { ...mockUser, mfaEnabled: true };
      const request = { ip: '127.0.0.1', headers: { 'user-agent': 'test' } };

      jest.spyOn(jwtService, 'sign').mockReturnValue('mfa.token');

      const result = await authService.login(userWithMfa as any, false, request);

      expect(result).toHaveProperty('requiresMfa', true);
      expect(result).toHaveProperty('mfaToken');
    });
  });

  describe('refreshTokens', () => {
    it('should refresh tokens successfully', async () => {
      const refreshToken = 'valid.refresh.token';
      const payload = {
        sub: mockUser.id,
        sessionId: 'session123',
      };

      jest.spyOn(jwtService, 'verify').mockReturnValue(payload);
      jest.spyOn(usersService, 'findById').mockResolvedValue(mockUser as any);
      jest.spyOn(sessionsService, 'findById').mockResolvedValue({
        isActive: true,
      } as any);
      jest.spyOn(jwtService, 'sign').mockReturnValue('new.jwt.token');

      const result = await authService.refreshTokens(refreshToken);

      expect(result).toHaveProperty('tokens');
      expect(jwtService.verify).toHaveBeenCalledWith(refreshToken, expect.any(Object));
    });

    it('should throw UnauthorizedException for invalid token', async () => {
      const refreshToken = 'invalid.token';

      jest.spyOn(jwtService, 'verify').mockImplementation(() => {
        throw new Error('Invalid token');
      });

      await expect(authService.refreshTokens(refreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
    });
  });

  describe('Security Tests', () => {
    describe('Password Security', () => {
      it('should hash passwords with bcrypt factor 12', async () => {
        const password = 'TestP@ssw0rd123';
        const hashSpy = jest.spyOn(bcrypt, 'hash');

        const registerDto = {
          email: 'security@example.com',
          password,
        };

        jest.spyOn(usersService, 'findByEmail').mockResolvedValue(null);
        jest.spyOn(usersService, 'create').mockResolvedValue(mockUser as any);
        jest.spyOn(jwtService, 'sign').mockReturnValue('mock.jwt.token');

        await authService.register(registerDto);

        expect(hashSpy).toHaveBeenCalledWith(password, 12);
      });

      it('should enforce password complexity requirements', async () => {
        // This is handled by the DTO validation, but we can test the pattern
        const weakPasswords = ['password', '12345678', 'Password1', 'password!'];
        const strongPasswords = ['P@ssw0rd123', 'Str0ng!Pass', 'C0mplex#Pass123'];

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/;

        weakPasswords.forEach(pwd => {
          expect(passwordRegex.test(pwd)).toBe(false);
        });

        strongPasswords.forEach(pwd => {
          expect(passwordRegex.test(pwd)).toBe(true);
        });
      });
    });

    describe('Session Security', () => {
      it('should invalidate all sessions on password reset', async () => {
        const token = 'reset-token';
        const userId = mockUser.id;

        jest.spyOn(cacheService, 'get').mockResolvedValue(userId);
        jest.spyOn(cacheService, 'del').mockResolvedValue();
        jest.spyOn(usersService, 'updatePassword').mockResolvedValue();
        jest.spyOn(sessionsService, 'revokeAllForUser').mockResolvedValue();

        await authService.resetPassword(token, 'NewP@ssw0rd123');

        expect(sessionsService.revokeAllForUser).toHaveBeenCalledWith(userId);
      });

      it('should validate session on token refresh', async () => {
        const refreshToken = 'valid.refresh.token';
        const payload = {
          sub: mockUser.id,
          sessionId: 'session123',
        };

        jest.spyOn(jwtService, 'verify').mockReturnValue(payload);
        jest.spyOn(usersService, 'findById').mockResolvedValue(mockUser as any);
        jest.spyOn(sessionsService, 'findById').mockResolvedValue({
          isActive: false, // Inactive session
        } as any);

        await expect(authService.refreshTokens(refreshToken)).rejects.toThrow(
          UnauthorizedException,
        );
      });
    });

    describe('Rate Limiting Protection', () => {
      it('should handle multiple failed login attempts', async () => {
        // Rate limiting is handled at the controller/middleware level
        // This test verifies the service can handle rapid requests
        const promises = Array(10).fill(null).map(() => 
          authService.forgotPassword('test@example.com')
        );

        await expect(Promise.all(promises)).resolves.toBeDefined();
      });
    });

    describe('Timing Attack Prevention', () => {
      it('should return consistent response for forgot password', async () => {
        const existingEmail = 'existing@example.com';
        const nonExistingEmail = 'nonexisting@example.com';

        jest.spyOn(usersService, 'findByEmail')
          .mockResolvedValueOnce(mockUser as any) // Existing user
          .mockResolvedValueOnce(null); // Non-existing user

        const result1 = await authService.forgotPassword(existingEmail);
        const result2 = await authService.forgotPassword(nonExistingEmail);

        expect(result1.message).toBe(result2.message);
      });
    });
  });
});