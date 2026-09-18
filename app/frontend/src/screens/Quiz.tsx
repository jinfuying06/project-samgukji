/**
 * S-006 Evidence-linked quiz. product/feature_spec.md L-04: exact item schema is `[TBD]`.
 * Per design/wireframe_brief.md's explicit instruction, this renders "퀴즈 준비 중" rather
 * than a guessed data contract — do not build against an invented schema.
 */
export function Quiz() {
  return (
    <section aria-label="근거 연동 퀴즈" role="status">
      <p>퀴즈 준비 중</p>
      <p className="quiz-tbd-note">
        퀴즈 항목 스키마는 아직 확정되지 않았습니다 (product/feature_spec.md L-04). 확정되면 이 화면을 구현합니다.
      </p>
    </section>
  );
}
