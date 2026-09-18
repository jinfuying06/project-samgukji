// jest-axe ships no TypeScript declarations; centralize the untyped import here
// so individual test files stay clean.
// @ts-expect-error jest-axe has no type declarations
import { axe as axeImpl, toHaveNoViolations as toHaveNoViolationsImpl } from "jest-axe";

export const axe: (container: Element | Document) => Promise<unknown> = axeImpl;
export const toHaveNoViolations = toHaveNoViolationsImpl;

interface AxeMatchers<R = unknown> {
  toHaveNoViolations(): R;
}

declare module "vitest" {
  interface Assertion<T = any> extends AxeMatchers<T> {} // eslint-disable-line @typescript-eslint/no-explicit-any
  interface AsymmetricMatchersContaining extends AxeMatchers {}
}
