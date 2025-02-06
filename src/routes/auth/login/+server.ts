import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export async function POST({ request }: RequestEvent) {
    const { email, password } = await request.json();

    return new Promise((resolve) => {
        db.get('SELECT * FROM users WHERE email = ? AND password = ?', 
            [email, password],
            (err, row) => {
                if (err || !row) {
                    resolve(json({ error: 'Invalid credentials' }, { status: 401 }));
                    return;
                }
                resolve(json({ success: true }));
            }
        );
    });
}