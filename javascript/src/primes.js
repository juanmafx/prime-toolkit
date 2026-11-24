const WITNESSES = [2n, 3n, 5n, 7n, 11n, 13n, 17n, 19n, 23n];
const SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23];
export const MAX_SIEVE_LIMIT = 100_000_000;

function modularPower(base, exponent, modulus) {
  let result = 1n;
  let factor = base % modulus;
  let remaining = exponent;
  while (remaining > 0n) {
    if (remaining & 1n) {
      result = (result * factor) % modulus;
    }
    factor = (factor * factor) % modulus;
    remaining >>= 1n;
  }
  return result;
}

function passesStrongTest(number, witness, oddPart, twos) {
  let value = modularPower(witness, oddPart, number);
  if (value === 1n || value === number - 1n) {
    return true;
  }
  for (let round = 1; round < twos; round += 1) {
    value = (value * value) % number;
    if (value === number - 1n) {
      return true;
    }
  }
  return false;
}

export function isPrime(number) {
  if (!Number.isSafeInteger(number)) {
    throw new RangeError('number must be a safe integer');
  }
  if (number < 2) {
    return false;
  }
  for (const prime of SMALL_PRIMES) {
    if (number % prime === 0) {
      return number === prime;
    }
  }
  const candidate = BigInt(number);
  let oddPart = candidate - 1n;
  let twos = 0;
  while ((oddPart & 1n) === 0n) {
    oddPart >>= 1n;
    twos += 1;
  }
  return WITNESSES.every((witness) => passesStrongTest(candidate, witness, oddPart, twos));
}

export function primesBelow(limit) {
  if (!Number.isSafeInteger(limit) || limit < 0 || limit > MAX_SIEVE_LIMIT) {
    throw new RangeError(`limit must be an integer between 0 and ${MAX_SIEVE_LIMIT}`);
  }
  if (limit <= 2) {
    return [];
  }
  const size = Math.floor(limit / 2);
  const composite = new Uint8Array(size);
  const primes = [2];
  for (let index = 1; index < size; index += 1) {
    if (composite[index] === 0) {
      const prime = 2 * index + 1;
      primes.push(prime);
      for (let multiple = 2 * index * (index + 1); multiple < size; multiple += prime) {
        composite[multiple] = 1;
      }
    }
  }
  return primes;
}
