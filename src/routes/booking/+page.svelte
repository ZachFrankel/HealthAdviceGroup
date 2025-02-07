<script lang="ts">
    interface User {
        name: string;
        email: string;
        password: string;
    }

    export let data: { user: User };
    const { user } = data;

    let address = '';
    let selectedDate = '';
    let selectedTime = '';
    let error = '';

    const availableSlots: { [key: string]: string[] } = {
        "01/02/2024": ["09:00", "10:00", "14:00", "15:00"],
        "02/02/2024": ["09:00", "11:00", "13:00", "16:00"],
        "03/02/2024": ["10:00", "11:00", "14:00", "15:00"]
    };

    let availableTimes: string[] = [];

    function handleDateChange() {
        availableTimes = selectedDate ? availableSlots[selectedDate] : [];
        selectedTime = '';
    }

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        
        if (!address || !selectedDate || !selectedTime) {
            error = 'Please fill in all fields';
            return;
        }

        const response = await fetch('/booking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: user.name,
                email: user.email,
                address,
                date: selectedDate,
                time: selectedTime
            })
        });

        if (response.ok) {
            return;
        } else {
            const data = await response.json();
            error = data.error;
        }
    }
</script>

<main class="min-h-screen bg-gray-50">
    <section class="relative bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-12 text-white">
        <div class="mx-auto max-w-6xl text-center">
            <h1 class="mb-6 text-4xl font-bold leading-tight">Book a Risk Assessment</h1>
            <p class="mb-8 text-xl opacity-90">Schedule a home visit with our qualified risk assessment experts</p>
        </div>
    </section>

    <section class="mx-auto max-w-4xl px-4 py-16">
        <div class="rounded-2xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 text-3xl font-bold text-gray-800">Book Risk Assessment</h1>

            <form class="space-y-4" onsubmit={handleSubmit}>
                <div>
                    <label for="fullName" class="block text-sm font-medium text-gray-700">Full Name</label>
                    <input
                        type="text"
                        id="fullName"
                        value={user.name}
                        disabled
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 bg-gray-100 text-gray-600 cursor-not-allowed"
                    />
                </div>

                <div>
                    <label for="address" class="block text-sm font-medium text-gray-700">Address</label>
                    <textarea
                        id="address"
                        bind:value={address}
                        rows="3"
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500"
                        placeholder="123 High Street&#10;London&#10;SW1A 1AA">
                    </textarea>
                </div>

                <div>
                    <label for="date" class="block text-sm font-medium text-gray-700">Date</label>
                    <select
                        id="date"
                        bind:value={selectedDate}
                        onchange={handleDateChange}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500">
                        <option value="">Select a date</option>
                        {#each Object.keys(availableSlots) as date}
                            <option value={date}>{date}</option>
                        {/each}
                    </select>
                </div>

                <div>
                    <label for="time" class="block text-sm font-medium text-gray-700">Time</label>
                    <select
                        id="time"
                        bind:value={selectedTime}
                        disabled={!selectedDate}
                        class="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500">
                        <option value="">Select a time</option>
                        {#each availableTimes as time}
                            <option value={time}>{time}</option>
                        {/each}
                    </select>
                </div>

                <button 
                    type="submit" 
                    class="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors">
                    Book Assessment
                </button>
            </form>
        </div>
    </section>
</main>