import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export async function POST({ request }: RequestEvent) {
    const { name, email, address, date, time } = await request.json();

    return new Promise((resolve) => {
        db.run(
            'INSERT INTO bookings (name, email, address, date, time) VALUES (?, ?, ?, ?, ?)',
            [name, email, address, date, time],
            (err) => {
                if (err) {
                    resolve(json({ error: 'Booking failed' }, { status: 500 }));
                    return;
                }
                resolve(json({ success: true }));
            }
        );
    });
}