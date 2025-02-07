<script lang="ts">
    import type { PageData } from './$types';

    interface HealthEntry {
        id: number;
        date: string;
        weight: number;
        blood_pressure: string;
        steps: number;
        notes?: string;
    }

    export let data: PageData;
    const { user, healthData } = data as { user: any, healthData: HealthEntry[] };

    let weight = '';
    let bloodPressure = '';
    let steps = '';
    let notes = '';

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        
        const response = await fetch('/dashboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: user.email,
                weight,
                bloodPressure,
                steps,
                notes
            })
        });

        if (response.ok) {
            window.location.reload();
        }
    }

    async function deleteEntry(id: number) {
        const response = await fetch('/dashboard', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        if (response.ok) {
            window.location.reload();
        }
    }
</script>

<main class="min-h-screen bg-gray-50">
    <section class="relative bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-12 text-white">
        <div class="mx-auto max-w-4xl text-center">
            <h1 class="mb-6 text-4xl font-bold leading-tight">Health Dashboard</h1>
            <p class="mb-8 text-xl opacity-90">Monitor and track your health metrics</p>
        </div>
    </section>

    <section class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div class="grid gap-8 md:grid-cols-2">
            <div class="rounded-2xl bg-white p-8 shadow-lg">
                <h2 class="mb-6 text-2xl font-bold text-gray-800">Add Health Data</h2>
                
                <form class="space-y-4" onsubmit={handleSubmit}>
                    <div>
                        <label for="weight" class="block text-sm font-medium text-gray-700">Weight (kg)</label>
                        <input
                            type="number"
                            id="weight"
                            bind:value={weight}
                            step="0.1"
                            class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Enter your weight"
                        />
                    </div>

                    <div>
                        <label for="bloodPressure" class="block text-sm font-medium text-gray-700">Blood Pressure</label>
                        <input
                            type="text"
                            id="bloodPressure"
                            bind:value={bloodPressure}
                            class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                            placeholder="e.g. 120/80"
                        />
                    </div>

                    <div>
                        <label for="steps" class="block text-sm font-medium text-gray-700">Daily Steps</label>
                        <input
                            type="number"
                            id="steps"
                            bind:value={steps}
                            class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Enter total steps"
                        />
                    </div>

                    <div>
                        <label for="notes" class="block text-sm font-medium text-gray-700">Notes</label>
                        <textarea
                            id="notes"
                            bind:value={notes}
                            rows="3"
                            class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                            placeholder="Any additional notes about your health today..."
                        ></textarea>
                    </div>

                    <button 
                        type="submit"
                        class="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors"
                    >
                        Save Health Data
                    </button>
                </form>
            </div>

            <div class="rounded-2xl bg-white p-8 shadow-lg">
                <div class="mb-6 flex items-center justify-between">
                    <h2 class="text-2xl font-bold text-gray-800">Health History</h2>
                    <span class="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-600">
                        {healthData.length} Entries
                    </span>
                </div>
                
                <div class="space-y-6">
                    {#if healthData.length > 0}
                        {#each healthData as entry}
                            <div class="relative rounded-xl border border-gray-100 bg-white p-6 shadow-sm transition-all hover:shadow-md">
                                <div class="mb-4 flex items-center justify-between border-b border-gray-100 pb-4">
                                    <div class="flex items-center gap-3">
                                        <div class="rounded-full bg-blue-100 p-2">
                                            <svg class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                        </div>
                                        <span class="font-semibold text-gray-900">{entry.date}</span>
                                    </div>
                                    <button 
                                        onclick={() => deleteEntry(entry.id)}
                                        class="rounded-full p-2 text-gray-400 hover:bg-red-50 hover:text-red-500"
                                        aria-label="Delete health entry"
                                    >
                                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </div>
            
                                <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
                                    <div class="flex flex-col">
                                        <span class="text-sm text-gray-500">Weight</span>
                                        <span class="mt-1 font-semibold text-gray-900">{entry.weight} kg</span>
                                    </div>
                                    
                                    <div class="flex flex-col">
                                        <span class="text-sm text-gray-500">Blood Pressure</span>
                                        <span class="mt-1 font-semibold text-gray-900">{entry.blood_pressure}</span>
                                    </div>
                                    
                                    <div class="flex flex-col">
                                        <span class="text-sm text-gray-500">Steps</span>
                                        <span class="mt-1 font-semibold text-gray-900">{entry.steps}</span>
                                    </div>
                                </div>
            
                                {#if entry.notes}
                                    <div class="mt-4 rounded-lg bg-gray-50 p-4">
                                        <span class="block text-sm font-medium text-gray-500">Notes</span>
                                        <p class="mt-1 text-gray-700">{entry.notes}</p>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    {:else}
                        <div class="flex flex-col items-center justify-center rounded-lg bg-gray-50 p-12 text-center">
                            <svg class="mb-4 h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                            <p class="mb-2 text-lg font-medium text-gray-900">No health data yet</p>
                            <p class="text-gray-500">Start tracking your health metrics using the form on the left</p>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    </section>
</main>