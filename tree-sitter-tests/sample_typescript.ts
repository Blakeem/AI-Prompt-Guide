/**
 * Sample TypeScript file for tree-sitter testing.
 * Tests various code patterns for analysis.
 */

import { EventEmitter } from 'events';
import * as fs from 'fs';

// Constants
export const MAX_CONNECTIONS = 10;
export const DEFAULT_PORT = 3000;
const UNUSED_SECRET = "secret123";  // Dead code candidate

// Interfaces
export interface UserConfig {
    id: string;
    name: string;
    email: string;
    settings?: Record<string, unknown>;
}

interface InternalConfig {
    debug: boolean;
    timeout: number;
}

// Types
type ConnectionState = 'connected' | 'disconnected' | 'pending';
type UnusedType = string | number;  // Dead code candidate

// Exported class
export class ConnectionManager extends EventEmitter {
    private connections: Map<string, Connection> = new Map();
    private config: InternalConfig;
    private state: ConnectionState = 'disconnected';

    constructor(config: InternalConfig) {
        super();
        this.config = config;
    }

    public connect(id: string): boolean {
        if (this.state === 'connected') {
            return true;
        }

        try {
            const conn = new Connection(id);
            this.connections.set(id, conn);
            this.state = 'connected';
            this.emit('connected', id);
            return true;
        } catch (error) {
            this.emit('error', error);
            return false;
        }
    }

    public disconnect(id: string): void {
        this.connections.delete(id);
        if (this.connections.size === 0) {
            this.state = 'disconnected';
        }
    }

    private internalHelper(): void {
        // Potentially unused private method
        console.log('helper');
    }

    public processData(data: unknown[]): unknown[] {
        // High complexity function
        const results: unknown[] = [];

        for (const item of data) {
            if (typeof item === 'object' && item !== null) {
                if ('type' in item) {
                    const typedItem = item as { type: string; value: unknown };
                    if (typedItem.type === 'a') {
                        if (typeof typedItem.value === 'number') {
                            if (typedItem.value > 100) {
                                results.push({ ...typedItem, processed: true });
                            } else if (typedItem.value > 50) {
                                results.push({ ...typedItem, partial: true });
                            } else {
                                results.push(typedItem);
                            }
                        }
                    } else if (typedItem.type === 'b') {
                        results.push({ ...typedItem, typeB: true });
                    }
                }
            } else if (typeof item === 'string') {
                results.push(item.toUpperCase());
            }
        }

        return results;
    }
}

// Internal class - not exported
class Connection {
    public readonly id: string;
    private createdAt: Date;

    constructor(id: string) {
        this.id = id;
        this.createdAt = new Date();
    }

    public getAge(): number {
        return Date.now() - this.createdAt.getTime();
    }
}

// Unused class - dead code candidate
class UnusedHelper {
    static format(value: string): string {
        return value.trim();
    }
}

// Exported functions
export function simpleFunction(x: number): number {
    return x * 2;
}

export function mediumComplexity(items: number[]): number[] {
    const result: number[] = [];

    for (const item of items) {
        if (item > 0) {
            result.push(item * 2);
        } else if (item < 0) {
            result.push(Math.abs(item));
        } else {
            result.push(0);
        }
    }

    return result;
}

// Function with many parameters - code smell
export function functionWithManyParams(
    a: number,
    b: string,
    c: boolean,
    d: object,
    e: unknown[],
    f: () => void,
    g?: string,
    h?: number
): void {
    console.log(a, b, c, d, e, f, g, h);
}

// Unused function - dead code
function unusedInternalFunction(): void {
    console.log('never called');
}

// Arrow functions
export const arrowSimple = (x: number): number => x * 2;

export const arrowComplex = (data: UserConfig[]): UserConfig[] => {
    return data.filter(user => {
        if (user.settings) {
            return Object.keys(user.settings).length > 0;
        }
        return false;
    });
};

// Higher-order function
export function createProcessor(multiplier: number): (x: number) => number {
    return (x: number) => x * multiplier;
}

// Async function
export async function fetchData(url: string): Promise<unknown> {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch failed:', error);
        throw error;
    }
}

// Module entry point
export function main(): void {
    const manager = new ConnectionManager({ debug: true, timeout: 5000 });
    manager.connect('user-1');

    simpleFunction(5);
    mediumComplexity([1, -2, 0, 3]);

    const processor = createProcessor(10);
    console.log(processor(5));
}
