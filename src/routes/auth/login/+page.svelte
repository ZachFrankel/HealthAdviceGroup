<script lang="ts">
    let email = '';
    let password = '';
</script>

<main class="min-h-screen bg-gray-50">
    <section class="mx-auto max-w-md px-4 py-16">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 text-3xl font-bold text-gray-800">Login</h1>

            <form class="space-y-4">
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                    <input
                        type="email"
                        id="email"
                        bind:value={email}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                    />
                </div>

                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                    <input
                        type="password"
                        id="password"
                        bind:value={password}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                    />
                </div>

                <button 
                    type="submit" 
                    class="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors"
                >
                    Login
                </button>
            </form>

            <p class="mt-4 text-center text-gray-600">
                Don't have an account? 
                <a href="/auth/register" class="text-blue-600 hover:underline">Register</a>
            </p>
        </div>
    </section>
</main>