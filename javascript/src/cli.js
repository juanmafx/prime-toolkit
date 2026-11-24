#!/usr/bin/env node
import { realpathSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { primesBelow } from './primes.js';

const DEFAULT_LIMIT = 10_000;

export function parseLimit(argument) {
  if (argument === undefined) {
    return DEFAULT_LIMIT;
  }
  if (!/^\d{1,9}$/.test(argument)) {
    throw new RangeError('limit must be a non-negative decimal integer');
  }
  return Number(argument);
}

export function run(argumentsList, write) {
  try {
    const primes = primesBelow(parseLimit(argumentsList[0]));
    if (primes.length > 0) {
      write(`${primes.join('\n')}\n`);
    }
    return 0;
  } catch (error) {
    if (error instanceof RangeError) {
      process.stderr.write(`error: ${error.message}\n`);
      return 2;
    }
    throw error;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  process.stdout.on('error', (error) => {
    if (error.code !== 'EPIPE') {
      throw error;
    }
    process.exit(0);
  });
  process.exitCode = run(process.argv.slice(2), (text) => process.stdout.write(text));
}
