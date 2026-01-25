/**
 * Consumer module to test cross-file reference detection.
 */

import {
    ConnectionManager,
    simpleFunction,
    mediumComplexity,
    MAX_CONNECTIONS,
    UserConfig,
    arrowSimple,
} from './sample_typescript';

// Note: UnusedHelper, unusedInternalFunction, functionWithManyParams NOT imported

export function useImports(): void {
    const manager = new ConnectionManager({ debug: false, timeout: 1000 });

    manager.connect('conn-1');

    const result = simpleFunction(42);
    const transformed = mediumComplexity([5, -3, 0]);

    console.log(`Max connections: ${MAX_CONNECTIONS}`);
    console.log(`Result: ${result}`);
    console.log(`Transformed: ${transformed}`);

    const doubled = arrowSimple(10);
    console.log(`Doubled: ${doubled}`);
}

export function processUsers(users: UserConfig[]): string[] {
    return users.map(user => user.name);
}
