<script lang="ts">
    import { onMount } from 'svelte';

    let city = 'London';
    let weatherData: any = null;
    let loading = false;
    let error = '';

    async function getWeather() {
        try {
            loading = true;
            error = '';

            const geoRes = await fetch(
                `https://api.openweathermap.org/geo/1.0/direct?q=${city}&limit=1&appid=${import.meta.env.VITE_WEATHER_API_KEY}`
            );

            if (!geoRes.ok) {
                throw new Error(`${geoRes.statusText}`);
            }

            const locations = await geoRes.json();
            if (!locations || locations.length === 0) {
                throw new Error('City not found');
            }

            const { lat, lon } = locations[0];

            const weatherRes = await fetch(
                `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${import.meta.env.VITE_WEATHER_API_KEY}`
            );

            if (!weatherRes.ok) {
                throw new Error(`Weather fetch failed: ${weatherRes.statusText}`);
            }

            weatherData = await weatherRes.json();
        } catch (err: any) {
            error = err.message || 'An error occurred';
            weatherData = null;
        } finally {
            loading = false;
        }
    }

    onMount(getWeather);
</script>

<main class="min-h-screen bg-gray-50">
    <section class="relative bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-12 text-white">
        <div class="mx-auto max-w-4xl text-center">
            <h1 class="mb-6 text-4xl font-bold leading-tight">Weather Forecast</h1>
            <p class="mb-8 text-xl opacity-90">Get accurate weather information for any city</p>
            
            <div class="mx-auto max-w-xl">
                <div class="flex gap-2 bg-white/10 backdrop-blur-sm p-2 rounded-full">
                    <input
                        type="text"
                        bind:value={city}
                        placeholder="Enter city name"
                        class="flex-1 rounded-full px-4 py-2 text-gray-800 border-0 focus:ring-2 focus:ring-blue-400"
                        on:keydown={(e) => e.key === 'Enter' && getWeather()}
                    />
                    <button
                        on:click={getWeather}
                        class="rounded-full bg-white px-6 py-2 font-semibold text-blue-600 hover:bg-opacity-90 disabled:opacity-50 transition-all"
                        disabled={loading}
                    >
                        {loading ? 'Searching...' : 'Search'}
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
        {:else if weatherData}
            <div class="rounded-2xl bg-white p-8 shadow-lg">
                <h2 class="mb-6 text-2xl font-bold text-gray-800">
                    Weather for {weatherData.city.name}, {weatherData.city.country}
                </h2>
                <div class="grid gap-6 md:grid-cols-3">
                    {#each weatherData.list.slice(0, 6) as forecast}
                        <div class="rounded-2xl bg-gray-50 p-6 shadow-md transition-shadow hover:shadow-lg">
                            <p class="text-lg font-semibold text-gray-800">
                                {new Date(forecast.dt * 1000).toLocaleDateString('en-GB')}
                            </p>
                            <p class="text-sm text-gray-600">
                                {new Date(forecast.dt * 1000).toLocaleTimeString('en-GB')}
                            </p>
                            <div class="my-4">
                                <p class="text-3xl font-bold text-blue-600">
                                    {Math.round(forecast.main.temp)}°C
                                </p>
                                <p class="capitalize text-gray-700">{forecast.weather[0].description}</p>
                            </div>
                            <div class="space-y-1 text-sm text-gray-600">
                                <p class="flex items-center gap-2">
                                    <span>Humidity:</span>
                                    <span class="font-medium">{forecast.main.humidity}%</span>
                                </p>
                                <p class="flex items-center gap-2">
                                    <span>Wind:</span>
                                    <span class="font-medium">{Math.round(forecast.wind.speed)} m/s</span>
                                </p>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </section>
</main>