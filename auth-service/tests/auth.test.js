const request = require('supertest');
const app = require('../src/index');

describe('Authentication Endpoints', () => {
    describe('POST /auth/register', () => {
        it('should register a new user', async () => {
            const res = await request(app)
                .post('/auth/register')
                .send({
                    email: 'test@example.com',
                    password: 'Test123!@#'
                });
            
            expect(res.statusCode).toBe(201);
            expect(res.body).toHaveProperty('message');
            expect(res.body.user).toHaveProperty('email');
        });
        
        it('should reject invalid email', async () => {
            const res = await request(app)
                .post('/auth/register')
                .send({
                    email: 'invalid-email',
                    password: 'Test123!@#'
                });
            
            expect(res.statusCode).toBe(400);
        });
        
        it('should reject weak password', async () => {
            const res = await request(app)
                .post('/auth/register')
                .send({
                    email: 'test@example.com',
                    password: '123'
                });
            
            expect(res.statusCode).toBe(400);
        });
    });
    
    describe('POST /auth/login', () => {
        it('should login with valid credentials', async () => {
            const res = await request(app)
                .post('/auth/login')
                .send({
                    email: 'test@example.com',
                    password: 'Test123!@#'
                });
            
            expect(res.statusCode).toBe(200);
            expect(res.body).toHaveProperty('token');
            expect(res.body).toHaveProperty('user');
        });
        
        it('should reject invalid credentials', async () => {
            const res = await request(app)
                .post('/auth/login')
                .send({
                    email: 'test@example.com',
                    password: 'wrongpassword'
                });
            
            expect(res.statusCode).toBe(401);
        });
    });
    
    describe('MFA Endpoints', () => {
        let authToken;
        
        beforeEach(async () => {
            const loginRes = await request(app)
                .post('/auth/login')
                .send({
                    email: 'test@example.com',
                    password: 'Test123!@#'
                });
            authToken = loginRes.body.token;
        });
        
        it('should setup MFA', async () => {
            const res = await request(app)
                .get('/auth/mfa/setup')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(res.statusCode).toBe(200);
            expect(res.body).toHaveProperty('secret');
            expect(res.body).toHaveProperty('qrCode');
        });
        
        it('should reject MFA setup without auth', async () => {
            const res = await request(app)
                .get('/auth/mfa/setup');
            
            expect(res.statusCode).toBe(401);
        });
    });
});
