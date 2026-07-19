export async function requestReflection(situation) {
    const response = await fetch('/api/reflections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ situation }),
    });
    if (!response.ok) {
        if (response.status === 422) {
            throw new Error('Please describe the situation in a little more detail.');
        }
        throw new Error('The reflection could not be prepared. Please try again.');
    }
    return response.json();
}
