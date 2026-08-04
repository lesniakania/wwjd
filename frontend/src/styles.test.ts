import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const styles = readFileSync("src/styles.css", "utf8");

describe("responsive styles", () => {
  it("gives the wordmark an intentionally organic shape", () => {
    expect(styles).toMatch(
      /\.wordmark-mark\s*\{[^}]*border-radius:\s*[^;]*%[^;]*%[^;]*%[^;]*%/s,
    );
    expect(styles).toMatch(
      /\.wordmark-mark-glyph\s*\{[^}]*transform:\s*translateX\(1px\)/s,
    );
    expect(styles).not.toMatch(/\.wordmark-mark-glyph\s*\{[^}]*rotate\(/s);
  });

  it("provides compact tablet and phone layouts", () => {
    expect(styles).toContain("@media (max-width: 820px)");
    expect(styles).toContain("@media (max-width: 480px)");
  });

  it("keeps long user-provided content inside narrow screens", () => {
    expect(styles).toMatch(/\.shared-question p[^}]*overflow-wrap:\s*anywhere/s);
    expect(styles).toMatch(/\.source-card[^}]*min-width:\s*0/s);
  });

  it("uses comfortable touch targets on phones", () => {
    const phoneStyles = styles.slice(styles.indexOf("@media (max-width: 480px)"));

    expect(phoneStyles).toMatch(/\.language-switch button[^}]*min-height:\s*44px/s);
    expect(phoneStyles).toMatch(/\.share-button[^}]*min-height:\s*44px/s);
    expect(phoneStyles).toMatch(/\.analytics-consent button[^}]*min-height:\s*44px/s);
  });
});
