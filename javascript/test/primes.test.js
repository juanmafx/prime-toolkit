import assert from 'node:assert/strict';
import { test } from 'node:test';
import { MAX_SIEVE_LIMIT, isPrime, primesBelow } from '../src/primes.js';
import { parseLimit, run } from '../src/cli.js';

function trialDivision(number) {
  if (number < 2) {
    return false;
  }
  for (let divisor = 2; divisor * divisor <= number; divisor += 1) {
    if (number % divisor === 0) {
      return false;
    }
  }
  return true;
}

function seededGenerator(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let mixed = Math.imul(state ^ (state >>> 15), 1 | state);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), 61 | mixed);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };
}

test('legacy false positives for zero, one, and negatives are fixed', () => {
  for (const value of [-7, -1, 0, 1]) {
    assert.equal(isPrime(value), false);
  }
});

test('known prime counts match', () => {
  for (const [limit, count] of [[10, 4], [100, 25], [10_000, 1_229], [1_000_000, 78_498]]) {
    assert.equal(primesBelow(limit).length, count);
  }
});

test('sieve boundaries are exclusive', () => {
  assert.deepEqual(primesBelow(0), []);
  assert.deepEqual(primesBelow(2), []);
  assert.deepEqual(primesBelow(3), [2]);
  assert.deepEqual(primesBelow(4), [2, 3]);
  assert.deepEqual(primesBelow(12), [2, 3, 5, 7, 11]);
});

test('isPrime agrees with sieve below 100000', () => {
  const primes = new Set(primesBelow(100_000));
  for (let value = 0; value < 100_000; value += 1) {
    assert.equal(isPrime(value), primes.has(value));
  }
});

test('Carmichael numbers and strong pseudoprimes are composite', () => {
  for (const value of [561, 1105, 1729, 41041, 825265, 2047, 1373653, 25326001, 3215031751]) {
    assert.equal(isPrime(value), false);
  }
});

test('large known primes near the safe integer ceiling', () => {
  assert.equal(isPrime(2147483647), true);
  assert.equal(isPrime(9007199254740881), true);
  assert.equal(isPrime(Number.MAX_SAFE_INTEGER), false);
});

test('seeded randomized agreement with trial division', () => {
  const next = seededGenerator(2026);
  for (let iteration = 0; iteration < 2000; iteration += 1) {
    const value = Math.floor(next() * 1_000_000_000_000);
    assert.equal(isPrime(value), trialDivision(value));
  }
});

test('invalid inputs throw', () => {
  for (const value of [1.5, Number.NaN, Number.MAX_SAFE_INTEGER + 1, '7']) {
    assert.throws(() => isPrime(value), RangeError);
  }
  for (const value of [-1, 1.5, MAX_SIEVE_LIMIT + 1]) {
    assert.throws(() => primesBelow(value), RangeError);
  }
});

test('cli parses limits and reports failures', () => {
  assert.equal(parseLimit(undefined), 10_000);
  assert.equal(parseLimit('25'), 25);
  assert.throws(() => parseLimit('1e3'), RangeError);
  let output = '';
  assert.equal(run(['12'], (text) => { output += text; }), 0);
  assert.equal(output, '2\n3\n5\n7\n11\n');
  assert.equal(run(['abc'], () => {}), 2);
});
