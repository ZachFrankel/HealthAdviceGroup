<script lang="ts">
    let fullName = '';
    let email = '';
    let password = '';
    let confirmPassword = '';
    let error = '';

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        if (password !== confirmPassword) {
            error = 'Passwords do not match';
            return;
        }

        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fullName, email, password })
        });

        if (response.ok) {
            window.location.href = '/auth/login';
        } else {
            const data = await response.json();
            error = data.error;
        }
    }
</script>

<main class="min-h-screen bg-gray-50">
    <section class="mx-auto max-w-md px-4 py-16">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 text-3xl font-bold text-gray-800">Create Account</h1>

            {#if error}
                <div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
            {/if}

            <form class="space-y-4" onsubmit={handleSubmit}>
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Full Name</label>
                    <input
                        type="text"
                        id="fullName"
                        bind:value={fullName}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                    />
                </div>

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

                <div>
                    <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        bind:value={confirmPassword}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                    />
                </div>

                <button 
                    type="submit" 
                    class="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors"
                >
                    Create Account
                </button>
            </form>

            <p class="mt-4 text-center text-gray-600">
                Already have an account? 
                <a href="/auth/login" class="text-blue-600 hover:underline">Login</a>
            </p>
        </div>
    </section>
</main>