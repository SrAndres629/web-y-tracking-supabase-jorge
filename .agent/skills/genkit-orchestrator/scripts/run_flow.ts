import { runFlow } from './index'; // assuming the flows are exported from the main index
import { z } from 'genkit';

async function main() {
    const flowName = process.argv[2];
    const inputJson = process.argv[3] || '{}';

    if (!flowName) {
        console.error('Usage: tsx run_flow.ts <flowName> [inputJson]');
        process.exit(1);
    }

    try {
        const input = JSON.parse(inputJson);
        console.log(`Running flow: ${flowName}...`);
        // Note: In a real implementation, we'd use the Genkit client or direct function call
        // This is a template for the actual runtime script.
        // const result = await runFlow(flowName, input);
        // console.log('Result:', JSON.stringify(result, null, 2));
        console.log('Flow execution script initialized. Connect to your flows in index.ts');
    } catch (error) {
        console.error('Execution failed:', error);
        process.exit(1);
    }
}

main();
