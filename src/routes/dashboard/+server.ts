import { json, type RequestEvent } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export async function POST({ request }: RequestEvent) {
    const { email, weight, bloodPressure, steps, notes } = await request.json();
    const date = new Date().toLocaleDateString('en-GB').split('T')[0];

    return new Promise((resolve) => {
        db.run(
            'INSERT INTO health_data (email, date, weight, blood_pressure, steps, notes) VALUES (?, ?, ?, ?, ?, ?)',
            [email, date, weight, bloodPressure, steps, notes],
            (err) => {
                if (err) {
                    resolve(json({ error: 'Failed to save health data' }, { status: 500 }));
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
            'DELETE FROM health_data WHERE id = ?',
            [id],
            (err) => {
                if (err) {
                    resolve(json({ error: 'Failed to delete entry' }, { status: 500 }));
                    return;
                }
                resolve(json({ success: true }));
            }
        );
    });
}