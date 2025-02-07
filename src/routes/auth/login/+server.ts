import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import bcrypt from 'bcrypt';

interface UserRow {
    id: number;
    email: string;
    password: string;
}

export async function POST({ request, cookies }: RequestEvent) {
    const { email, password } = await request.json();

    return new Promise((resolve) => {
        db.get('SELECT * FROM users WHERE email = ?', 
            [email],
            async (err, row: UserRow) => {
                if (err || !row) {
                    resolve(json({ error: 'Invalid credentials' }, { status: 401 }));
                    return;
                }

                const match = await bcrypt.compare(password, row.password);
                if (!match) {
                    resolve(json({ error: 'Invalid credentials' }, { status: 401 }));
                    return;
                }

                cookies.set('session', row.id.toString(), {
                    path: '/',
                    httpOnly: true,
                    sameSite: 'strict',
                    secure: process.env.NODE_ENV === 'production',
                    maxAge: 60 * 60 * 24 * 7 // 1 week
                });
                
                resolve(json({ success: true }));
            }
        );
    });
}