import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { getUserFromSession } from '$lib/server/auth';
import { db } from '$lib/server/db';

interface User {
    email: string;
}

export const load: PageServerLoad = async (event) => {
    const user = await getUserFromSession(event) as User;
    
    if (!user) {
        throw redirect(302, '/auth/login');
    }

    const healthData = await new Promise((resolve) => {
        db.all(
            'SELECT * FROM health_data WHERE email = ? ORDER BY date DESC',
            [user.email],
            (err, rows) => {
                if (err) resolve([]);
                else resolve(rows);
            }
        );
    });

    return { user, healthData };
};