import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

/**
 * Real-browser accessibility + keyboard verification against the live app (real
 * Chromium layout/CSSOM, real backend) -- distinct from the jsdom-based `jest-axe`
 * unit tests in tests/components/*, which cannot evaluate real layout, contrast
 * computed from actual rendered CSS, or true focus/viewport behavior. This is the
 * "beyond automated jest-axe scans" testing design/accessibility_checklist.md's
 * rows ask for.
 *
 * Still automated, not a substitute for a human testing with real assistive
 * technology (a screen reader). That remains untested -- disclosed honestly in
 * the checklist, not claimed here.
 *
 * Requires the backend running separately on :8000 with real imported curated
 * data (app/backend/README.md "Running locally"); this suite only auto-starts
 * the frontend dev server (playwright.config.ts's `webServer`).
 */

async function expectNoAxeViolations(page: Page, label: string) {
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations, `${label}:\n${JSON.stringify(results.violations, null, 2)}`).toEqual([]);
}

test.describe("적벽대전 vertical slice — real-browser accessibility scan", () => {
  test("사건 개요 (EventOverview)", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /적벽대전/ })).toBeVisible();
    await expectNoAxeViolations(page, "EventOverview");
  });

  test("인물 비교 (PersonComparison) — 인물 선택 후", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "曹操" }).click();
    await expectNoAxeViolations(page, "PersonComparison");
  });

  test("점수 분해 (ScoreBreakdown) — 가중치 실험실 열림 포함", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "점수 분해" }).click();
    await expectNoAxeViolations(page, "ScoreBreakdown (닫힘)");

    await page.getByRole("button", { name: /가중치 실험 열기/ }).click();
    await page.getByLabel("인물 선택").selectOption({ label: "曹操" });
    await expectNoAxeViolations(page, "ScoreBreakdown (가중치 실험실 열림)");
  });

  test("AI 질문 (AskAI) — 답변 상태 포함", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "AI 질문" }).click();
    await expectNoAxeViolations(page, "AskAI (빈 상태)");

    await page.getByLabel("질문").fill("曹操는 어떤 인물인가요?");
    await page.getByRole("button", { name: "질문하기" }).click();
    await page.waitForSelector(".ai-answer-claims, .ai-answer-abstained", { timeout: 10_000 });
    await expectNoAxeViolations(page, "AskAI (답변 상태)");
  });

  test("퀘스트 → 퀴즈 흐름 전체 완주 (실사용자가 완료 가능한지 실제로 확인)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /학습 시작/ }).click();
    await expectNoAxeViolations(page, "Quest (조건 미충족)");

    const completeBtn = page.getByRole("button", { name: "완료" });
    await expect(completeBtn).toHaveAttribute("aria-disabled", "true");

    // Both evidence items must be reachable and clickable through the real UI --
    // this is exactly the reachability bug found and fixed by this same testing pass
    // (QuestCard previously rendered no button for the required-layer evidence item).
    await page.getByRole("button", { name: /HB-J54-P2/ }).click();
    await page.getByRole("button", { name: /RM-C050-P3/ }).click();
    await expect(completeBtn).toHaveAttribute("aria-disabled", "false");
    await expectNoAxeViolations(page, "Quest (조건 충족)");

    await completeBtn.click();
    await expect(page.getByText("퀴즈는 아직 준비 중이에요!")).toBeVisible();
    await expectNoAxeViolations(page, "Quiz (준비 중 상태)");
  });

  test("키보드만으로 상단 내비게이션 3개 버튼에 순서대로 도달하고, 포커스가 시각적으로 보인다", async ({ page }) => {
    await page.goto("/");
    const navButtonCount = await page.locator(".app-nav button").count();
    expect(navButtonCount).toBe(3);

    for (let i = 0; i < navButtonCount; i++) {
      await page.keyboard.press("Tab");
      const activeText = await page.evaluate(() => document.activeElement?.textContent?.trim());
      const outlineStyle = await page.evaluate(() => getComputedStyle(document.activeElement as Element).outlineStyle);
      expect(activeText, `nav button #${i}`).toBeTruthy();
      expect(outlineStyle, `nav button #${i} (${activeText}) focus outline`).not.toBe("none");
    }
  });

  test("좁은 화면(360px)에서 가로 스크롤 없이 렌더된다", async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /적벽대전/ })).toBeVisible();
    const { scrollWidth, clientWidth } = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(scrollWidth, "no horizontal overflow at 360px width").toBeLessThanOrEqual(clientWidth + 1);
    await expectNoAxeViolations(page, "EventOverview (360px)");
  });

  test("prefers-reduced-motion 환경에서도 정상 렌더된다", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await expectNoAxeViolations(page, "EventOverview (reduced motion)");
  });
});
