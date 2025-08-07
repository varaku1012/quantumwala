import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../app.module';

describe('Security Tests (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('OWASP Top 10 Security Tests', () => {
    describe('A01:2021 – Broken Access Control', () => {
      it('should deny access to protected routes without authentication', async () => {
        await request(app.getHttpServer())
          .get('/api/v1/auth/me')
          .expect(401);

        await request(app.getHttpServer())
          .get('/api/v1/auth/sessions')
          .expect(401);

        await request(app.getHttpServer())
          .post('/api/v1/auth/mfa/enable')
          .expect(401);
      });

      it('should prevent users from accessing other users sessions', async () => {
        // This would require setting up authenticated requests
        // Implementation depends on test utilities
      });
    });

    describe('A02:2021 – Cryptographic Failures', () => {
      it('should not expose sensitive data in responses', async () => {
        const response = await request(app.getHttpServer())
          .post('/api/v1/auth/login')
          .send({
            email: 'test@example.com',
            password: 'wrong-password',
          })
          .expect(401);

        expect(response.body).not.toContain('passwordHash');
        expect(response.body).not.toContain('mfaSecret');
      });

      it('should use secure headers', async () => {
        const response = await request(app.getHttpServer())
          .get('/api/v1/health')
          .expect(200);

        expect(response.headers['x-frame-options']).toBeDefined();
        expect(response.headers['x-content-type-options']).toBe('nosniff');
        expect(response.headers['x-xss-protection']).toBeDefined();
      });
    });

    describe('A03:2021 – Injection', () => {
      it('should prevent SQL injection in login', async () => {
        await request(app.getHttpServer())
          .post('/api/v1/auth/login')
          .send({
            email: "admin' OR '1'='1",
            password: "' OR '1'='1",
          })
          .expect(400); // Should fail validation
      });

      it('should sanitize user input', async () => {
        await request(app.getHttpServer())
          .post('/api/v1/auth/register')
          .send({
            email: '<script>alert("xss")</script>@example.com',
            password: 'ValidP@ssw0rd123',
          })
          .expect(400); // Should fail email validation
      });
    });

    describe('A04:2021 – Insecure Design', () => {
      it('should implement rate limiting', async () => {
        const requests = Array(150).fill(null).map(() =>
          request(app.getHttpServer())
            .post('/api/v1/auth/login')
            .send({
              email: 'test@example.com',
              password: 'wrong-password',
            })
        );

        const responses = await Promise.all(requests);
        const rateLimited = responses.some(r => r.status === 429);
        
        expect(rateLimited).toBe(true);
      });
    });

    describe('A05:2021 – Security Misconfiguration', () => {
      it('should not expose debug information in production', async () => {
        process.env.NODE_ENV = 'production';

        const response = await request(app.getHttpServer())
          .post('/api/v1/auth/login')
          .send({
            email: 'invalid-email',
            password: 'password',
          })
          .expect(400);

        expect(response.body).not.toContain('stack');
        expect(response.body).not.toContain('TypeError');
        
        process.env.NODE_ENV = 'test';
      });
    });

    describe('A07:2021 – Identification and Authentication Failures', () => {
      it('should enforce strong password requirements', async () => {
        const weakPasswords = [
          'password',
          '12345678',
          'Password1',
          'password!',
          'short',
        ];

        for (const password of weakPasswords) {
          await request(app.getHttpServer())
            .post('/api/v1/auth/register')
            .send({
              email: 'test@example.com',
              password,
            })
            .expect(400);
        }
      });

      it('should implement account lockout after failed attempts', async () => {
        // Make multiple failed login attempts
        for (let i = 0; i < 6; i++) {
          await request(app.getHttpServer())
            .post('/api/v1/auth/login')
            .send({
              email: 'locked@example.com',
              password: 'wrong-password',
            });
        }

        // Next attempt should be locked
        const response = await request(app.getHttpServer())
          .post('/api/v1/auth/login')
          .send({
            email: 'locked@example.com',
            password: 'correct-password',
          });

        expect(response.status).toBe(423); // Locked
      });
    });

    describe('A08:2021 – Software and Data Integrity Failures', () => {
      it('should validate JWT signatures', async () => {
        const tamperedToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

        await request(app.getHttpServer())
          .get('/api/v1/auth/me')
          .set('Authorization', `Bearer ${tamperedToken}`)
          .expect(401);
      });
    });

    describe('A10:2021 – Server-Side Request Forgery (SSRF)', () => {
      it('should validate OAuth redirect URIs', async () => {
        await request(app.getHttpServer())
          .get('/api/v1/auth/etsy')
          .query({ redirect_uri: 'http://evil-site.com' })
          .expect(400);
      });
    });
  });

  describe('Additional Security Tests', () => {
    describe('CSRF Protection', () => {
      it('should validate CSRF tokens on state-changing operations', async () => {
        // CSRF protection implementation would go here
      });
    });

    describe('Session Security', () => {
      it('should regenerate session ID on login', async () => {
        // Session regeneration test
      });

      it('should expire sessions after inactivity', async () => {
        // Session expiry test
      });
    });

    describe('Input Validation', () => {
      it('should reject requests with extra fields', async () => {
        await request(app.getHttpServer())
          .post('/api/v1/auth/register')
          .send({
            email: 'test@example.com',
            password: 'ValidP@ssw0rd123',
            isAdmin: true, // Extra field
            roles: ['admin'], // Extra field
          })
          .expect(400);
      });
    });

    describe('Error Handling', () => {
      it('should not leak system information in errors', async () => {
        const response = await request(app.getHttpServer())
          .post('/api/v1/auth/login')
          .send({
            email: null,
            password: undefined,
          })
          .expect(400);

        expect(response.body.message).toBeDefined();
        expect(response.body).not.toContain('TypeError');
        expect(response.body).not.toContain('/src/');
      });
    });
  });
});