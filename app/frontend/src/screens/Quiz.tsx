/**
 * S-006 Evidence-linked quiz. product/feature_spec.md L-04: exact item schema is `[TBD]`.
 * Per design/wireframe_brief.md's explicit instruction, this renders "퀴즈 준비 중" rather
 * than a guessed data contract — do not build against an invented schema.
 */
export function Quiz() {
  return (
    <section aria-label="근거 연동 퀴즈" role="status">
      <h1>퀴즈</h1>
      <p>퀴즈는 아직 준비 중이에요!</p>
      <p className="quiz-tbd-note">
        곧 여기에서 방금 확인한 근거를 가지고 문제를 풀어볼 수 있게 될 거예요. 문제가 정확히 어떤 모양일지는
        아직 정해지지 않아서 (product/feature_spec.md L-04), 정해지는 대로 진짜로 만들 거예요 — 미리 지어내지
        않아요.
      </p>
    </section>
  );
}
