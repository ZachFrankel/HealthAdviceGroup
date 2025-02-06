import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export async function POST({ request }: RequestEvent) {
    const { email, password } = await request.json();

    return new Promise((resolve) => {
        db.get('SELECT * FROM users WHERE email = ?', [email], (err, row) => {
            if (row) {
                resolve(json({ error: 'Email already exists' }, { status: 400 }));
                return;
            }

            db.run('INSERT INTO users (email, password) VALUES (?, ?)', 
                [email, password],
                (err) => {
                    if (err) {
                        resolve(json({ error: 'Registration failed' }, { status: 500 }));
                        return;
                    }
                    resolve(json({ success: true }));
                }
            );
        });
    });
}