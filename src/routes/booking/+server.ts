import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export async function POST({ request }: RequestEvent) {
    const { name, email, address, date, time } = await request.json();
    const status = 'pending';

    return new Promise((resolve) => {
        db.run(
            'INSERT INTO bookings (name, email, address, date, time, status) VALUES (?, ?, ?, ?, ?, ?)',
            [name, email, address, date, time, status],
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

export async function DELETE({ request }: RequestEvent) {
    const { id } = await request.json();

    return new Promise((resolve) => {
        db.run(
            'UPDATE bookings SET status = ? WHERE id = ? AND status = ?',
            ['cancelled', id, 'pending'],
            (err) => {
                if (err) {
                    resolve(json({ error: 'Cancellation failed' }, { status: 500 }));
                    return;
                }
                resolve(json({ success: true }));
            }
        );
    });
}