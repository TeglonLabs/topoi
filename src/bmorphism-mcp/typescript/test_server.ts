import { Server } from './server';

describe('Clojure Metaphors in TypeScript', () => {
  let server: Server;

  beforeEach(() => {
    server = new Server();
  });

  test('Immutable Foundations', () => {
    /* Like bedrock beneath a mountain, immutability provides stability */
    expect(server.getState()).toBe('initial');
    expect(() => {
      // @ts-expect-error - Testing immutability
      server.state = 'modified';
    }).toThrow();
  });

  test('Functional Streams', () => {
    /* Like a river's current, data flows without side effects */
    const result = server.processData([1, 2, 3]);
    expect(result).toEqual([2, 3, 4]);
    expect(server.getData()).toEqual([1, 2, 3]);
  });

  test('Composition as Symbiosis', () => {
    /* Like symbiotic relationships, functions work together harmoniously */
    const composed = server.composeFunctions(
      (x: number) => x + 1,
      (x: number) => x * 2
    );
    expect(composed(3)).toBe(8); // (3 + 1) * 2
  });

  test('Persistent Growth', () => {
    /* Like a tree adding rings, we grow without destroying the past */
    const original = server.getData();
    const modified = server.updateData(4);
    expect(modified).toEqual([1, 2, 3, 4]);
    expect(server.getData()).toEqual(original);
  });

  test('Higher-Order Wisdom', () => {
    /* Like a wise elder passing down knowledge, functions teach functions */
    const transform = server.createTransformer((x: number) => x * 2);
    expect(transform([1, 2, 3])).toEqual([2, 4, 6]);
  });
});
