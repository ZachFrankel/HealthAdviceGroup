import type { RequestEvent } from '@sveltejs/kit';
import { db } from './db';

export function getUserFromSession(event: RequestEvent) {
    const sessionId = event.cookies.get('session');
    if (!sessionId) return null;

    return new Promise((resolve) => {
        db.get('SELECT * FROM users WHERE id = ?', [sessionId], (err, row) => {
            resolve(row || null);
        });
    });
}