import { describe, expect, it } from "vitest";
import { Language, copyFor } from "./localization";

describe("localization", () => {
  it("returns copy for each supported language", () => {
    expect(copyFor(Language.Polish).submit).toBe("Znajdź drogę naprzód");
    expect(copyFor(Language.English).submit).toBe("Find a way forward");
  });

  it("provides the complete algorithm explanation in both languages", () => {
    for (const language of [Language.Polish, Language.English]) {
      const copy = copyFor(language);
      expect(copy.algorithmSteps).toHaveLength(6);
      expect(copy.algorithmTitle).toBeTruthy();
      expect(copy.algorithmIntro).toBeTruthy();
      expect(copy.algorithmSafeguard).toBeTruthy();
    }
  });
});
