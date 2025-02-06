<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	let { children } = $props();
</script>

<Navbar />
<main class="mx-auto">
	{@render children()}
</main>