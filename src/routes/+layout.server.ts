import { getUserFromSession } from '$lib/server/auth';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async (event) => {
    const user = await getUserFromSession(event);
    return {
        user
    };
};