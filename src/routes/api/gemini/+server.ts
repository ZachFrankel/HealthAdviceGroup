import { json } from '@sveltejs/kit';
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash' });

export async function POST({ request }) {
    try {
        const { prompt } = await request.json();
        const result = await model.generateContent(prompt);
        const response = await result.response;
        return json({ response: response.text() });
    } catch (error) {
        console.error('Gemini API error:', error);
        return json({ error: 'Failed to get AI response' }, { status: 500 });
    }
}