<script lang="ts">
    import { GoogleGenerativeAI } from '@google/generative-ai';

    let result: string | null = null;
    let query = '';
    let loading = false;
    let error = '';

    async function getAdvice() {
        loading = true;
        try {
            const response = await fetch('/api/gemini', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: query })
            });
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            loading = data.response;
        } catch (error) {
            result = 'Sorry, something went wrong. Please try again.';
        } finally {
            loading = false;
        }
    }
</script>

<main class="min-h-screen bg-gray-50">
    <section class="relative bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-12 text-white">
        <div class="mx-auto max-w-4xl text-center">
            <h1 class="mb-6 text-4xl font-bold leading-tight">Health Advice Portal</h1>
            <p class="mb-8 text-xl opacity-90">Get personalised health recommendations</p>
            
            <div class="mx-auto max-w-xl">
                <div class="flex gap-2 bg-white/10 backdrop-blur-sm p-2 rounded-full">
                    <input
                        type="text"
                        bind:value={query}
                        placeholder="Ask a health related question..."
                        class="flex-1 rounded-full px-4 py-2 text-gray-800 border-0 focus:ring-2 focus:ring-blue-400"
                        on:keydown={(e) => e.key === 'Enter' && getAdvice()}
                    />
                    <button
                        on:click={getAdvice}
                        class="rounded-full bg-white px-6 py-2 font-semibold text-blue-600 hover:bg-opacity-90 disabled:opacity-50 transition-all"
                        disabled={loading}
                    >
                        {loading ? 'Thinking...' : 'Ask'}
                    </button>
                </div>
            </div>
        </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {#if error}
            <div class="rounded-2xl bg-red-50 p-6 text-red-700 shadow-lg">
                <p class="font-semibold">{error}</p>
            </div>
        {:else if result}
            <div class="rounded-2xl bg-white p-8 shadow-lg">
                <h2 class="mb-6 text-2xl font-bold text-gray-800">Answer</h2>
                <div class="prose max-w-none text-gray-600">
                    {result}
                </div>
            </div>
        {/if}
    </section>
</main>