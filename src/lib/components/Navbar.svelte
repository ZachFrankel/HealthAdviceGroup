<script lang="ts">
    import { page } from '$app/stores';

    async function handleLogout() {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/';
    }
</script>

<nav class="bg-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4">
        <div class="flex h-16">
            <a href="/" class="flex items-center text-xl font-bold text-gray-800 hover:text-blue-600 transition-colors">Health Advice Group</a>

            <div class="flex-1 flex justify-center items-center space-x-8">
                <a href="/" class="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-blue-600 {$page.url.pathname === '/' ? 'border-b-2 border-blue-600' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/></svg>
                    <span>Home</span>
                </a>
                <a href="/weather" class="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-blue-600 {$page.url.pathname === '/weather' ? 'border-b-2 border-blue-600' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M5.5 16a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.977A4.5 4.5 0 1113.5 16h-8z"/></svg>
                    <span>Weather</span>
                </a>
                <a href="/advice" class="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-blue-600 {$page.url.pathname === '/advice' ? 'border-b-2 border-blue-600' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
                    <span>Advice</span>
                </a>
                <a href="/booking" class="flex items-center space-x-2 px-3 py-2 text-gray-700 hover:text-blue-600 {$page.url.pathname === '/booking' ? 'border-b-2 border-blue-600' : ''}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/></svg>
                    <span>Risk Assessments</span>
                </a>
            </div>

            <div class="flex items-center space-x-4">
                {#if $page.data.user}
                    <a href="/dashboard" class="px-3 py-2 text-gray-700 hover:text-blue-600">Dashboard</a>
                    <button on:click={handleLogout} class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors">Logout</button>
                {:else}
                    <a href="/auth/login" class="px-3 py-2 text-gray-700 hover:text-blue-600">Login</a>
                    <a href="/auth/register" class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors">Register</a>
                {/if}
            </div>
        </div>
    </div>
</nav>